import asyncio
import json
from pathlib import Path
from app.services.auth_service import reddit_login
from app.services.scrape_service import scrape_user_profile, scrape_subreddit_about
from app.services.storage_service import upsert_username_list, upsert_subreddit_info
from app.utils.logger import logger
from app.db.database import init_db
# from settings import REDDIT_USER, REDDIT_PASS, HF_API_KEY
from app.ai_client import generate_message
from app.utils.proxy_manager import get_next_working_proxy, proxies_list
import itertools
import httpx

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

USERNAME = "daniellikescoffee123"
PASSWORD = "RNeixv617fjv6nJ*Yfc+q3k!3R"

async def login_and_get_cookies():
    """Face login o singură dată și returnează cookies + headers."""
    async with httpx.AsyncClient() as base_session:
        logged_in, _ = await reddit_login(USERNAME, PASSWORD, session=base_session)
        if not logged_in:
            return None, None
        cookies = base_session.cookies.jar
        headers = base_session.headers.copy()
    return cookies, headers

async def create_sessions_with_proxies(cookies, headers):
    """Creează câte o sesiune httpx pentru fiecare proxy și le rotește."""
    sessions = []
    for proxy in proxies_list:
        client = httpx.AsyncClient(
            proxies={"http://": proxy, "https://": proxy},
            timeout=30
        )
        client.cookies.update(cookies)
        client.headers.update(headers)
        sessions.append(client)
    return itertools.cycle(sessions)  # rotație infinită

async def run_orchestration():
    logger.info("🚀 Pornim orchestratorul Reddit")
    logger.info(str(CONFIG_FILE))

    init_db()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    users = cfg.get("users", [])
    subreddits = cfg.get("subreddits", [])

    # Login o singură dată
    cookies, headers = await login_and_get_cookies()
    if not cookies:
        logger.error("❌ Autentificarea a eșuat. Oprire proces.")
        return

    # Creăm sesiunile cu proxy-uri diferite
    session_cycle = await create_sessions_with_proxies(cookies, headers)

    # Users
    for user in users:
        session = next(session_cycle)
        user_data = await scrape_user_profile(user, session=session)
        if user_data:
            upsert_username_list([user_data])

    # Subreddits
    for sub in subreddits:
        session = next(session_cycle)
        sub_data = await scrape_subreddit_about(sub, session=session)
        # if sub_data:
        #     upsert_subreddit_info(sub_data)

    logger.info("🏁 Orchestrator finalizat cu succes")

if __name__ == "__main__":
    asyncio.run(run_orchestration())

