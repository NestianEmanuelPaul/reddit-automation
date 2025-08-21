import asyncio
import json
from pathlib import Path
from app.services.auth_service import reddit_login
from app.services.scrape_service import scrape_user_profile, scrape_subreddit_about
from app.services.storage_service import upsert_username_list, upsert_subreddit_info
from app.utils.logger import logger
from app.db.database import init_db
from settings import REDDIT_USERNAME, REDDIT_PASSWORD, HF_API_KEY

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

USERNAME = REDDIT_USERNAME
PASSWORD = REDDIT_PASSWORD

async def run_orchestration():
    logger.info("🚀 Pornim orchestratorul Reddit")
    logger.info(str(CONFIG_FILE))

    # Init DB (creează tabelele dacă nu există)
    init_db()

    # Config
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    users = cfg.get("users", [])
    subreddits = cfg.get("subreddits", [])

    # Login
    logged_in, session = await reddit_login(USERNAME, PASSWORD)
    if not session:
        logger.error("❌ Autentificarea a eșuat. Oprire proces.")
        return

    # Users
    for user in users:
        user_data = await scrape_user_profile(user, session=session)
        if user_data:
            upsert_username_list([user_data])

    # Subreddits
    for sub in subreddits:
        sub_data = await scrape_subreddit_about(sub, session=session)
        if sub_data:
            upsert_subreddit_info(sub_data)

    logger.info("🏁 Orchestrator finalizat cu succes")

if __name__ == "__main__":
    asyncio.run(run_orchestration())

