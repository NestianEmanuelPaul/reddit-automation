import asyncio
import json
from pathlib import Path
from app.services.auth_service import reddit_login
from app.services.scrape_service import scrape_user_profile, scrape_subreddit_about
from app.services.storage_service import upsert_username_list, upsert_subreddit_info
from app.utils.logger import logger
from app.db.database import init_db
from app.ai_client import generate_message
from app.utils.proxy_manager import get_next_working_proxy, proxies_list
import itertools
import httpx

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

USERNAME = "daniellikescoffee123"
PASSWORD = "RNeixv617fjv6nJ*Yfc+q3k!3R"

async def login_and_get_cookies(proxy=None):
    """Face login și returnează cookies + headers, cu sau fără proxy."""
    if proxy:
        logger.info(f"🌐 Login folosind proxy: {proxy}")
        async with httpx.AsyncClient(proxy=proxy, timeout=30) as base_session:
            logged_in, _ = await reddit_login(USERNAME, PASSWORD, session=base_session)
            if not logged_in:
                return None, None
            cookies = base_session.cookies.jar
            headers = base_session.headers.copy()
        return cookies, headers
    else:
        logger.info("🌐 Login fără proxy")
        async with httpx.AsyncClient(timeout=30) as base_session:
            logged_in, _ = await reddit_login(USERNAME, PASSWORD, session=base_session)
            if not logged_in:
                return None, None
            cookies = base_session.cookies.jar
            headers = base_session.headers.copy()
        return cookies, headers

async def create_sessions_with_proxies(cookies, headers):
    """
    Creează câte o sesiune httpx pentru fiecare proxy funcțional.
    Dacă niciun proxy nu e funcțional, face fallback la o singură sesiune fără proxy.
    Returnează întotdeauna un itertools.cycle cu cel puțin o sesiune.
    """
    sessions = []

    # încearcă fiecare proxy din listă; păstrează doar cele funcționale
    for proxy in proxies_list:
        # folosim testerul tău; dacă nu e funcțional, îl sărim
        try:
            working = await get_next_working_proxy(start_proxy=proxy)
        except TypeError:
            # dacă signătura funcției tale e fără start_proxy, folosește rotația internă
            working = await get_next_working_proxy()

        if not working:
            logger.warning(f"⚠️ Proxy {proxy} nu este funcțional, îl sar.")
            continue

        client = httpx.AsyncClient(proxy=working, timeout=30)
        client.cookies.update(cookies)
        client.headers.update(headers)
        setattr(client, "proxy_url", working)
        sessions.append(client)

    if not sessions:
        logger.warning("⚠️ Niciun proxy funcțional — folosesc o sesiune fără proxy pentru scraping.")
        client = httpx.AsyncClient(timeout=30)
        client.cookies.update(cookies)
        client.headers.update(headers)
        setattr(client, "proxy_url", None)
        sessions.append(client)

    return itertools.cycle(sessions)  # rotație (măcar 1 element)

async def run_orchestration():
    logger.info("🚀 Pornim orchestratorul Reddit")
    logger.info(str(CONFIG_FILE))

    init_db()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    users = cfg.get("users", [])
    subreddits = cfg.get("subreddits", [])

    # 1) determină un proxy funcțional (dacă există) pentru login
    try:
        login_proxy = await get_next_working_proxy()
    except TypeError:
        # compatibil cu implementarea ta fără parametri
        login_proxy = await get_next_working_proxy()

    if not login_proxy:
        logger.warning("⚠️ Niciun proxy funcțional — login fără proxy")
        cookies, headers = await login_and_get_cookies(proxy=None)
    else:
        cookies, headers = await login_and_get_cookies(proxy=login_proxy)

    if not cookies:
        logger.error("❌ Autentificarea a eșuat. Oprire proces.")
        return

    # 2) creează rotația de sesiuni (cu fallback garantat fără proxy)
    session_cycle = await create_sessions_with_proxies(cookies, headers)

    # 3) Users
    for user in users:
        session = next(session_cycle)
        proxy_label = getattr(session, "proxy_url", None)
        if proxy_label:
            logger.info(f"📋 [Scraping] Folosesc proxy: {proxy_label}")
        else:
            logger.info("📋 [Scraping] Fără proxy")
        user_data = await scrape_user_profile(user, session=session)
        if user_data:
            upsert_username_list([user_data])

    # 4) Subreddits
    for sub in subreddits:
        session = next(session_cycle)
        proxy_label = getattr(session, "proxy_url", None)
        if proxy_label:
            logger.info(f"📋 [Scraping] Folosesc proxy: {proxy_label}")
        else:
            logger.info("📋 [Scraping] Fără proxy")
        sub_data = await scrape_subreddit_about(sub, session=session)
        # if sub_data:
        #     upsert_subreddit_info(sub_data)

    logger.info("🏁 Orchestrator finalizat cu succes")

if __name__ == "__main__":
    asyncio.run(run_orchestration())
