from app.utils.logger import logger
from app.utils.http_client import fetch_with_retry  # hook global pentru toate cererile

BASE_URL = "https://www.reddit.com"

async def scrape_user_profile(username: str, session):
    """
    Preia informațiile 'about' ale unui user Reddit.
    Primește un obiect session (ex: httpx.AsyncClient) deja autentificat.
    """
    if not session or not hasattr(session, "get"):
        logger.error(f"[SCRAPE USER] Sesiune invalidă pentru {username}, skip.")
        return None

    try:
        url = f"{BASE_URL}/user/{username}/about.json"
        logger.info(f"🔍 Colectez date despre utilizator: {username}")

        resp = await fetch_with_retry("GET", url, session=session)
        logger.info(f"✅ Date preluate cu succes pentru {username} (status={resp.status_code})")


        return resp.json()

    except Exception as e:
        logger.error(f"Eroare la scraping pentru {username}: {type(e).__name__} -> {e}")
        return None


async def scrape_subreddit_about(subreddit: str, session):
    """
    Preia informațiile 'about' ale unui subreddit.
    """
    if not session or not hasattr(session, "get"):
        logger.error(f"[SCRAPE SUB] Sesiune invalidă pentru r/{subreddit}, skip.")
        return None

    try:
        url = f"{BASE_URL}/r/{subreddit}/about.json"
        logger.info(f"🔍 Colectez date despre subreddit: {subreddit}")

        resp = await fetch_with_retry("GET", url, session=session)
        logger.info(f"✅ Date preluate cu succes pentru r/{subreddit} (status={resp.status_code})")

        return resp.json()

    except Exception as e:
        logger.error(f"Eroare la scraping pentru r/{subreddit}: {type(e).__name__} -> {e}")
        return None
