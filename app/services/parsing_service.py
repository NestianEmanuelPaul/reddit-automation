# =========================
# Importuri necesare
# =========================
import re  # pentru expresii regulate (extrage numele de utilizator din URL)
from typing import List, Dict, Any  # tipare pentru claritate
from bs4 import BeautifulSoup  # pentru parsarea HTML-ului
from httpx import AsyncClient  # client HTTP asincron
from app.utils.logger import logger  # logger-ul centralizat al aplicației

# =========================
# Constante globale
# =========================
BASE_URL = "https://www.reddit.com"  # URL-ul de bază pentru Reddit
HEADERS = {"User-Agent": "Mozilla/5.0"}  # antet pentru a evita blocarea request-urilor

# =========================
# Funcție internă: _fetch_user_about
# =========================
async def _fetch_user_about(session: AsyncClient, username: str) -> Dict[str, Any]:
    """
    Preia datele complete pentru un utilizator din endpoint-ul /about.json.
    - Folosește un request GET asincron.
    - Returnează un dicționar cu toate câmpurile relevante.
    - În caz de eroare, returnează un set minim de date pentru a nu bloca fluxul.
    """
    url = f"{BASE_URL}/user/{username}/about.json"
    try:
        # Trimite request către Reddit
        resp = await session.get(url, headers=HEADERS, timeout=10.0)
        resp.raise_for_status()  # ridică excepție dacă status != 200

        # Extrage secțiunea "data" din JSON
        data = resp.json().get("data", {})

        # Returnează datele utilizatorului
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
        # Loghează eroarea și returnează date minime
        logger.error(f"❌ Eroare la preluarea /about.json pentru {username}: {e}")
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

# =========================
# Funcție publică: get_recent_users
# =========================
async def get_recent_users(
    session: AsyncClient,
    subreddit: str = "AskReddit",
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Returnează o listă de dicționare cu date complete din /about.json
    pentru utilizatorii extrași din pagina 'new' a unui subreddit.
    - Face scraping pe pagina HTML a subreddit-ului.
    - Extrage link-urile către profilurile utilizatorilor.
    - Apelează _fetch_user_about pentru fiecare user, în paralel.
    """
    url = f"{BASE_URL}/r/{subreddit}/new/"
    logger.info(f"📥 Preiau date din {url}")

    try:
        # Request asincron către pagina 'new' a subreddit-ului
        resp = await session.get(url, headers=HEADERS, timeout=15.0)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"❌ Eroare la accesarea {url}: {e}")
        return []

    # Parsează HTML-ul primit
    soup = BeautifulSoup(resp.text, "html.parser")

    usernames = []  # listă finală de username-uri
    seen = set()    # set pentru a evita duplicatele

    # Selectează toate link-urile care duc la /user/<username>
    for a in soup.select("a[href^='/user/']"):
        match = re.match(r"^/user/([^/]+)/?$", a["href"])
        if match:
            uname = match.group(1)
            if uname not in seen:
                seen.add(uname)
                usernames.append(uname)
        # Oprește dacă am atins limita cerută
        if len(usernames) >= limit:
            break

    logger.info(f"✅ Găsit {len(usernames)} useri unici. Preiau detalii din /about.json...")

    # Importă gather pentru a rula request-urile în paralel
    from asyncio import gather
    users_data = await gather(*[
        _fetch_user_about(session, uname) for uname in usernames
    ])

    return users_data
