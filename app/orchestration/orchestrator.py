# =========================
# Importuri standard și din aplicație
# =========================
import asyncio          # pentru rularea funcțiilor asincrone
import json             # pentru citirea fișierului de configurare config.json
from pathlib import Path  # pentru lucrul cu căi de fișiere în mod portabil

# Servicii interne pentru login și scraping
from app.services.auth_service import reddit_login
from app.services.scrape_service import scrape_user_profile, scrape_subreddit_about

# Servicii interne pentru stocare în DB
from app.services.storage_service import upsert_username_list, upsert_subreddit_info

# Logger-ul aplicației
from app.utils.logger import logger

# Inițializare DB
from app.db.database import init_db

# Manager de proxy-uri
from app.utils.proxy_manager import get_next_working_proxy, proxies_list

import itertools        # pentru a crea un ciclu infinit de sesiuni
import httpx            # client HTTP asincron
import os
from dotenv import load_dotenv  # pentru încărcarea variabilelor din .env
from colorama import Fore, Style  # pentru colorarea logurilor

# =========================
# Încărcare variabile de mediu
# =========================
load_dotenv()

# Directorul curent al fișierului și calea către config.json
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

# Citirea credentialelor Reddit din .env
USERNAME = os.getenv("REDDIT_USER")
PASSWORD = os.getenv("REDDIT_PASS")

# =========================
# Funcție: login_and_get_cookies
# =========================
async def login_and_get_cookies(proxy=None):
    """
    Face login pe Reddit și returnează cookies + headers.
    Dacă primește un proxy, folosește acel proxy pentru login.
    """
    if proxy:
        logger.info(f"⚠️ {Fore.GREEN}📋 Login folosind proxy: {proxy}{Style.RESET_ALL}")
        async with httpx.AsyncClient(proxy=proxy, timeout=30) as base_session:
            logged_in, _ = await reddit_login(USERNAME, PASSWORD, session=base_session)
            if not logged_in:
                return None, None
            cookies = base_session.cookies.jar
            headers = base_session.headers.copy()
        return cookies, headers
    else:
        logger.info(f"🌐 {Fore.RED}Login fără proxy{Style.RESET_ALL}")
        async with httpx.AsyncClient(timeout=30) as base_session:
            logged_in, _ = await reddit_login(USERNAME, PASSWORD, session=base_session)
            if not logged_in:
                return None, None
            cookies = base_session.cookies.jar
            headers = base_session.headers.copy()
        return cookies, headers

# =========================
# Funcție: create_sessions_with_proxies
# =========================
async def create_sessions_with_proxies(cookies, headers):
    """
    Creează câte o sesiune httpx pentru fiecare proxy funcțional.
    Dacă niciun proxy nu e funcțional, creează o singură sesiune fără proxy.
    Returnează un itertools.cycle cu cel puțin o sesiune (rotație infinită).
    """
    sessions = []

    # Testează fiecare proxy din lista globală
    for proxy in proxies_list:
        try:
            # Încearcă să obțină un proxy funcțional pornind de la acesta
            working = await get_next_working_proxy(start_proxy=proxy)
        except TypeError:
            # Dacă funcția nu acceptă parametru, folosește rotația internă
            working = await get_next_working_proxy()

        if not working:
            logger.warning(f"⚠️ Proxy {proxy} nu este funcțional, îl sar.")
            continue

        # Creează client HTTPX cu proxy-ul funcțional
        client = httpx.AsyncClient(proxy=working, timeout=30)
        client.cookies.update(cookies)
        client.headers.update(headers)
        setattr(client, "proxy_url", working)  # salvează proxy-ul în obiect pentru loguri
        sessions.append(client)
        logger.info(f"✅ {Fore.GREEN}Sesiune adăugată pentru proxy: {working}{Style.RESET_ALL}")

    # Dacă nu există niciun proxy funcțional, folosește conexiune directă
    if not sessions:
        logger.warning("⚠️ Niciun proxy funcțional — folosesc o sesiune fără proxy pentru scraping.")
        client = httpx.AsyncClient(timeout=30)
        client.cookies.update(cookies)
        client.headers.update(headers)
        setattr(client, "proxy_url", None)
        sessions.append(client)
        logger.info(f"✅ {Fore.GREEN}Sesiune adăugată fără proxy{Style.RESET_ALL}")

    # Returnează un ciclu infinit de sesiuni (round-robin)
    return itertools.cycle(sessions)

# =========================
# Funcția principală: run_orchestration
# =========================
async def run_orchestration():
    """
    Orchestratorul principal:
    - Inițializează DB
    - Citește config.json pentru lista de useri și subreddits
    - Face login pe Reddit (cu sau fără proxy)
    - Creează sesiuni HTTPX (cu rotație de proxy-uri)
    - Rulează scraping pentru fiecare user și subreddit
    - Salvează datele în DB
    """
    logger.info("🚀 Pornim orchestratorul Reddit")
    logger.info(str(CONFIG_FILE))

    # Inițializează baza de date
    init_db()

    # Citește fișierul de configurare
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    users = cfg.get("users", [])
    subreddits = cfg.get("subreddits", [])

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

    # 3) Creează rotația de sesiuni (cu fallback fără proxy)
    session_cycle = await create_sessions_with_proxies(cookies, headers)

    # 4) Scraping pentru useri
    for user in users:
        session = next(session_cycle)
        proxy_label = getattr(session, "proxy_url", None)
        if proxy_label:
            logger.info(f"📋 {Fore.BLUE}[Scraping] Folosesc proxy: {proxy_label}{Style.RESET_ALL}")
        else:
            logger.info("📋 [Scraping] Fără proxy")
        user_data = await scrape_user_profile(user, session=session)
        if user_data:
            upsert_username_list([user_data])

    # 5) Scraping pentru subreddits
    for sub in subreddits:
        session = next(session_cycle)
        proxy_label = getattr(session, "proxy_url", None)
        if proxy_label:
            logger.info(f"📋 [Scraping] Folosesc proxy: {proxy_label}")
        else:
            logger.info("📋 [Scraping] Fără proxy")
        sub_data = await scrape_subreddit_about(sub, session=session)
        # Dacă vrei să salvezi info despre subreddit, decomentează linia de mai jos
        # if sub_data:
        #     upsert_subreddit_info(sub_data)

    logger.info("🏁 Orchestrator finalizat cu succes")

# =========================
# Rulează orchestratorul direct dacă fișierul e executat standalone
# =========================
if __name__ == "__main__":
    asyncio.run(run_orchestration())
