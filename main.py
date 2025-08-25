import threading
import time
from datetime import datetime
import requests
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import sys

# === Importurile tale existente ===
from app.routers import health, metrics, test_flow
from app.api import endpoints
from app.utils.logger import logger
from app.orchestration.orchestrator import run_orchestration
from app.scraper import collect_new_users, enrich_with_activity
from app.filter import filter_online_users, filter_all_users
from app.suggest import SuggestRequest, SuggestResponse, suggest_for_user
from colorama import init, Fore, Style

# === Importuri pentru autentificare și alerte ===
from app.auth_manager import get_session, login
from app.telegram_alert import send_telegram_alert

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# === Configurări monitor ===
CHECK_INTERVAL = 10  # secunde
running = True
relogin_done = threading.Event()
is_logged_in = True

# === App FastAPI ===
app = FastAPI()

# --- Include rutele existente ---
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(test_flow.router)
app.include_router(endpoints.router)

init(autoreset=True)

# === Funcții monitorizare ===
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def check_login():
    global is_logged_in
    try:
        get_session()
        return True
    except Exception:
        is_logged_in = False
        return False

def relogin():
    global is_logged_in
    logger.info(f"[{datetime.now():%H:%M:%S}] 🔄 Relogin...")
    login()
    is_logged_in = True
    relogin_done.set()
    logger.info(f"[{datetime.now():%H:%M:%S}] ✅ Relogin reușit.")
    send_telegram_alert("✅ Reconectare efectuată cu succes.")

def monitor():
    global is_logged_in
    while running:
        ok_net = check_internet()
        ok_login = check_login()

        if not ok_net or not ok_login:
            problem = "Internet" if not ok_net else "Login"
            logger.warning(f"[{datetime.now():%H:%M:%S}] ⚠️ Problemă {problem} detectată.")
            send_telegram_alert(f"❌ Problemă {problem} — încerc reconectare...")
            is_logged_in = False
            relogin()
        else:
            logger.info(f"[{datetime.now():%H:%M:%S}] ✅ Monitor OK")

        time.sleep(CHECK_INTERVAL)

# === Bucla principală de lucru ===
def main_loop():
    max_loops = 1
    loop_count = 0
    global is_logged_in
    while running and loop_count < max_loops:
        loop_count += 1
        if not is_logged_in:
            logger.info("[INFO] Aștept reconectare...")
            relogin_done.wait(timeout=30)
            relogin_done.clear()

        try:
            # Orchestrarea principală
            awaitable = False
            try:
                import inspect
                if inspect.iscoroutinefunction(run_orchestration):
                    awaitable = True
            except:
                pass

            if awaitable:
                import asyncio
                asyncio.run(run_orchestration())
            else:
                run_orchestration()

            # === Colectare și filtrare cohortă ===
            # === Colectare useri noi ===
            users = collect_new_users(max_users=100)
            logger.info(f"{Fore.CYAN}📋 Am găsit {len(users)} useri noi{Style.RESET_ALL}")

            # === Îmbogățire date ===
            logger.info(f"[DEBUG] Pornesc enrich_with_activity pentru {len(users)} useri")

            full_data = enrich_with_activity(users)
            logger.info(f"{Fore.CYAN}📋 Am îmbogățit datele pentru {len(full_data)} useri{Style.RESET_ALL}")

            # === Filtrare cohortă ===
            cohort = filter_online_users(full_data, max_users=20)
            if len(cohort) < 20:
                cohort = filter_all_users(full_data, max_users=20)
            logger.info(f"{Fore.MAGENTA}📋 Cohorta finală ({len(cohort)} useri):{Style.RESET_ALL}")
            for u, info in cohort.items():
                logger.info(f"{Fore.YELLOW}- {u} | Online: {info.get('is_online')}{Style.RESET_ALL}")
        
                # === Sugestii AI ===
                features = {
                    "karma": info.get("karma", 0),
                    "joined_days": info.get("joined_days", 0)
                }
                history = info.get("comments", [])

                ai_resp = suggest_for_user(u, features, history)
                if ai_resp and hasattr(ai_resp, "suggestions"):
                    for s in ai_resp.suggestions:
                        logger.info(f"{Fore.GREEN}[AI->{u}] {s.message} (score={s.score}){Style.RESET_ALL}")
                else:
                    logger.warning(f"{Fore.RED}[AI->{u}] Nicio sugestie generată{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"{Fore.RED}[E] Eroare în main_loop: {e}{Style.RESET_ALL}")
            break


# === Evenimente FastAPI ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("🚀 Pornire server și monitor...")
    threading.Thread(target=monitor, daemon=True).start()
    threading.Thread(target=main_loop, daemon=True).start()

    yield  # 🔹 Aici rulează aplicația

    # --- Shutdown ---
    global running
    print("🛑 Oprire server...")
    running = False

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(test_flow.router)
app.include_router(endpoints.router)

@app.get("/")
async def root():
    return {"message": "Salut!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

# === Endpoint manual pentru orchestrare ===
@app.post("/run-orchestration")
async def run_orch():
    await run_orchestration()
    return {"status": "done"}

@app.post("/suggest", response_model=SuggestResponse)
async def suggest_endpoint(req: SuggestRequest):
    try:
        return suggest_for_user(req.user_id, req.features, req.history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
