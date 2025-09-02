# =========================
# Importuri din aplicație
# =========================
from app.utils.logger import logger  # logger-ul centralizat al aplicației
from app.utils.http_client import fetch_with_retry  # funcție utilitară pentru request-uri HTTP cu retry automat

# =========================
# Constante
# =========================
BASE_URL = "https://www.reddit.com"  # URL-ul de bază pentru API-ul public Reddit

# =========================
# Funcție: scrape_user_profile
# =========================
async def scrape_user_profile(username: str, session):
    """
    Preia informațiile 'about' ale unui user Reddit.
    Parametri:
      - username: numele utilizatorului Reddit
      - session: obiect httpx.AsyncClient deja autentificat (cu cookie-uri/token)
    Returnează:
      - dict cu datele JSON ale profilului, sau None în caz de eroare
    """
    # Verifică dacă sesiunea este validă și are metoda .get
    if not session or not hasattr(session, "get"):
        logger.error(f"[SCRAPE USER] Sesiune invalidă pentru {username}, skip.")
        return None

    try:
        # Construiește URL-ul endpoint-ului JSON pentru profilul userului
        url = f"{BASE_URL}/user/{username}/about.json"
        # logger.info(f"🔍 Colectez date despre utilizator: {username}")

        # Face request GET cu retry automat
        resp = await fetch_with_retry("GET", url, session=session)
        # logger.info(f"✅ Date preluate cu succes pentru {username} (status={resp.status_code})")

        # Returnează conținutul JSON
        return resp.json()

    except Exception as e:
        # Loghează orice eroare apărută în timpul scraping-ului
        logger.error(f"Eroare la scraping pentru {username}: {type(e).__name__} -> {e}")
        return None

# =========================
# Funcție: scrape_subreddit_about
# =========================
async def scrape_subreddit_about(subreddit: str, session):
    """
    Preia informațiile 'about' ale unui subreddit.
    Parametri:
      - subreddit: numele subreddit-ului (fără prefixul r/)
      - session: obiect httpx.AsyncClient deja autentificat
    Returnează:
      - dict cu datele JSON ale subreddit-ului, sau None în caz de eroare
    """
    # Verifică dacă sesiunea este validă
    if not session or not hasattr(session, "get"):
        logger.error(f"[SCRAPE SUB] Sesiune invalidă pentru r/{subreddit}, skip.")
        return None

    try:
        # Construiește URL-ul endpoint-ului JSON pentru pagina "about" a subreddit-ului
        url = f"{BASE_URL}/r/{subreddit}/about.json"
        # logger.info(f"🔍 Colectez date despre subreddit: {subreddit}")

        # Face request GET cu retry automat
        resp = await fetch_with_retry("GET", url, session=session)
        # logger.info(f"✅ Date preluate cu succes pentru r/{subreddit} (status={resp.status_code})")

        # Returnează conținutul JSON
        return resp.json()

    except Exception as e:
        # Loghează eroarea și returnează None
        logger.error(f"Eroare la scraping pentru r/{subreddit}: {type(e).__name__} -> {e}")
        return None
