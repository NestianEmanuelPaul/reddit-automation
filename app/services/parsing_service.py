# app/services/parsing_service.py
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from httpx import AsyncClient
from app.utils.logger import logger

BASE_URL = "https://www.reddit.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}


async def _fetch_user_about(session: AsyncClient, username: str) -> Dict[str, Any]:
    """
    Preia datele complete pentru un user din /about.json
    """
    url = f"{BASE_URL}/user/{username}/about.json"
    try:
        resp = await session.get(url, headers=HEADERS, timeout=10.0)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "reddit_id": data.get("id"),
            "name": data.get("name"),
            "total_karma": data.get("total_karma", 0),
            "link_karma": data.get("link_karma", 0),
            "comment_karma": data.get("comment_karma", 0),
            "created_utc": data.get("created_utc", 0.0),
            "is_employee": data.get("is_employee", False),
            "is_gold": data.get("is_gold", False),
            "is_mod": data.get("is_mod", False),
            "verified": data.get("verified", False),
            "icon_img": data.get("icon_img"),
            "public_description": data.get("subreddit", {}).get("public_description"),
        }
    except Exception as e:
        logger.error(f"❌ Eroare la preluarea /about.json pentru {username}: {e}")
        # Returnăm un minim ca să nu blocăm întregul flux
        return {
            "reddit_id": None,
            "name": username,
            "total_karma": 0,
            "link_karma": 0,
            "comment_karma": 0,
            "created_utc": 0.0,
            "is_employee": False,
            "is_gold": False,
            "is_mod": False,
            "verified": False,
            "icon_img": None,
            "public_description": None,
        }


async def get_recent_users(
    session: AsyncClient,
    subreddit: str = "AskReddit",
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Returnează o listă de dicționare cu date complete din /about.json
    pentru utilizatorii extrași din pagina 'new' a unui subreddit.
    """
    url = f"{BASE_URL}/r/{subreddit}/new/"
    logger.info(f"📥 Preiau date din {url}")

    try:
        resp = await session.get(url, headers=HEADERS, timeout=15.0)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"❌ Eroare la accesarea {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    usernames = []
    seen = set()

    for a in soup.select("a[href^='/user/']"):
        match = re.match(r"^/user/([^/]+)/?$", a["href"])
        if match:
            uname = match.group(1)
            if uname not in seen:
                seen.add(uname)
                usernames.append(uname)
        if len(usernames) >= limit:
            break

    logger.info(f"✅ Găsit {len(usernames)} useri unici. Preiau detalii din /about.json...")

    # Facem fetch în paralel pentru datele fiecărui user
    from asyncio import gather
    users_data = await gather(*[
        _fetch_user_about(session, uname) for uname in usernames
    ])

    return users_data
