# =========================
# Importuri standard Python
# =========================
import threading          # pentru a rula funcții în thread-uri separate (monitor, main_loop)
import time               # pentru pauze și timpi de așteptare
from datetime import datetime  # pentru timestamp-uri în loguri
import requests           # pentru verificarea conexiunii la internet
from fastapi import FastAPI, HTTPException  # framework API + gestionare erori HTTP
from contextlib import asynccontextmanager  # pentru definirea lifecycle-ului aplicației
import uvicorn            # server ASGI pentru a rula aplicația FastAPI
import asyncio            # pentru rularea funcțiilor asincrone
import sys                # pentru verificarea platformei și setarea politicii event loop
from colorama import Fore, Style  # pentru colorarea logurilor

# =========================
# Importuri din aplicația ta
# =========================
from app.routers import health, metrics, test_flow  # rute API predefinite
from app.api import endpoints                       # alte endpoint-uri API
from app.utils.logger import logger                 # logger configurat custom
from app.orchestration.orchestrator import run_orchestration  # orchestratorul principal
from app.scraper import collect_new_users, enrich_with_activity  # funcții de scraping și îmbogățire date
from app.filter import filter_online_users, filter_all_users     # funcții de filtrare a userilor
from app.suggest import SuggestRequest, SuggestResponse, suggest_for_user  # sugestii AI
from colorama import init, Fore, Style              # pentru colorarea textului în loguri
from app.orchestration.orchestrator import login_and_get_cookies

# =========================
# Importuri pentru autentificare și alerte
# =========================
from app.auth_manager import get_session, login     # gestionarea sesiunii și login-ului
from app.telegram_alert import send_telegram_alert  # trimitere alerte pe Telegram

# =========================
# Configurare event loop pentru Windows
# =========================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# =========================
# Configurări globale
# =========================
CHECK_INTERVAL = 10  # interval în secunde pentru verificările monitorului
running = True       # flag global pentru oprirea thread-urilor
relogin_done = threading.Event()  # eveniment pentru sincronizarea relogin-ului
is_logged_in = True  # stare curentă de login

# =========================
# Inițializare aplicație FastAPI
# =========================
app = FastAPI()

# Adăugare rute API
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(test_flow.router)
app.include_router(endpoints.router)

# Inițializare colorama pentru reset automat culori
init(autoreset=True)

# Manager de proxy-uri
from app.utils.proxy_manager import get_next_working_proxy, proxies_list

# =========================
# Funcții de monitorizare
# =========================

# Verifică dacă există conexiune la internet
def check_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

# Verifică dacă sesiunea de login este validă
def check_login():
    global is_logged_in
    try:
        get_session()
        return True
    except Exception:
        is_logged_in = False
        return False

# Reface login-ul și trimite alertă pe Telegram
def relogin():
    global is_logged_in
    logger.info(f"[{datetime.now():%H:%M:%S}] 🔄 Relogin...")
    login()
    is_logged_in = True
    relogin_done.set()
    logger.info(f"[{datetime.now():%H:%M:%S}] ✅ Relogin reușit.")
    send_telegram_alert("✅ Reconectare efectuată cu succes.")

# Monitorizează conexiunea la internet și login-ul, rulează continuu în thread separat
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

# =========================
# Bucla principală de lucru
# =========================
async def main_loop():
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
            # Rulează orchestratorul (sincron sau asincron)
            """ awaitable = False
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
                run_orchestration() """

            # Colectează useri noi
            users = collect_new_users(max_users=100)
            logger.info(f"{Fore.CYAN}📋 Am găsit {len(users)} useri noi{Style.RESET_ALL}")

            # 1) Determină un proxy funcțional pentru login
            try:
                login_proxy = await get_next_working_proxy()
            except TypeError:
                login_proxy = await get_next_working_proxy()

            # 2) Login cu sau fără proxy
            if not login_proxy:
                logger.warning(f"⚠️ {Fore.RED}📋 Niciun proxy funcțional — login fără proxy{Style.RESET_ALL}")
                cookies, headers = await login_and_get_cookies(proxy=None)
            else:
                logger.info(f"⚠️ {Fore.GREEN}📋 Avem proxy funcțional — {login_proxy}{Style.RESET_ALL}")
                cookies, headers = await login_and_get_cookies(proxy=login_proxy)

            if not cookies:
                logger.error("❌ Autentificarea a eșuat. Oprire proces.")
                return

            # Îmbogățește datele userilor
            logger.info(f"[DEBUG] Pornesc enrich_with_activity pentru {len(users)} useri")
            full_data = await enrich_with_activity(users, cookies, headers)
            logger.info(f"{Fore.CYAN}📋 Am îmbogățit datele pentru {len(full_data)} useri{Style.RESET_ALL}")

            # Filtrează cohorta de useri
            cohort = filter_online_users(full_data, max_users=20)
            if len(cohort) < 20:
                cohort = filter_all_users(full_data, max_users=20)
            logger.info(f"{Fore.MAGENTA}📋 Cohorta finală ({len(cohort)} useri):{Style.RESET_ALL}")

            # Generează sugestii AI pentru fiecare user din cohortă
            for u, info in cohort.items():
                logger.info(f"{Fore.YELLOW}- {u} | Online: {info.get('is_online')}{Style.RESET_ALL}")
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

# =========================
# Lifecycle FastAPI
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pornește monitorul și bucla principală în thread-uri separate
    print("🚀 Pornire server și monitor...")
    threading.Thread(target=monitor, daemon=True).start()
    threading.Thread(target=lambda: asyncio.run(main_loop()), daemon=True).start()

    yield  # aici rulează aplicația

    # Shutdown: oprește thread-urile
    global running
    print("🛑 Oprire server...")
    running = False

# Creează aplicația FastAPI cu lifecycle definit
app = FastAPI(lifespan=lifespan)

# Include rutele API
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(test_flow.router)
app.include_router(endpoints.router)

# Endpoint simplu GET pentru rădăcină
@app.get("/")
async def root():
    return {"message": "Salut!"}

# Pornire server direct din script (dacă e rulat ca main)
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

# Endpoint manual pentru a rula orchestratorul
@app.post("/run-orchestration")
async def run_orch():
    await run_orchestration()
    return {"status": "done"}

# Endpoint pentru sugestii AI
@app.post("/suggest", response_model=SuggestResponse)
async def suggest_endpoint(req: SuggestRequest):
    try:
        return suggest_for_user(req.user_id, req.features, req.history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
