# app/scraper.py

import asyncio
from app.services.auth_service import reddit_login   # Funcție pentru autentificare pe Reddit
from app.services.parsing_service import get_recent_users  # Funcție care extrage utilizatori recenți dintr-un subreddit
from app.services.storage_service import upsert_username_list  # Funcție care salvează/actualizează userii în DB
from app.utils.logger import logger  # Logger pentru mesaje structurate
from app.orchestration.orchestrator import create_sessions_with_proxies
# from settings import REDDIT_USER, REDDIT_PASS, HF_API_KEY
import time
import requests
from itertools import islice, cycle
import os
from dotenv import load_dotenv  # Pentru a încărca variabilele din fișierul .env

# Încarcă variabilele de mediu din fișierul .env
load_dotenv()

# Citim user și parolă din .env (folosite la login pe Reddit)
USERNAME = os.getenv("REDDIT_USER")
PASSWORD = os.getenv("REDDIT_PASS")

# ------------------- FLUX PRINCIPAL ASINCRON -------------------
async def main():
    print("[INFO] Pornim procesul de login...")
    # Autentificare pe Reddit (returnează True/False + sesiunea)
    logged_in, session = await reddit_login(USERNAME, PASSWORD)
    if not logged_in:
        print("[EROARE] Login eșuat. Oprire.")
        return

    print("[OK] Login reușit! Începem scraping utilizatori...")
    # Extragem utilizatori recenți din subreddit-ul AskReddit (max 50)
    users = await get_recent_users(session, subreddit="AskReddit", limit=50)
    print(f"[INFO] Am găsit {len(users)} utilizatori.")

    if users:
        # Salvăm/actualizăm lista de useri în baza de date
        upsert_username_list(users)  # Lista conține dict-uri cu reddit_id + câmpuri
        print("[OK] Lista de useri a fost salvată în DB.")
    else:
        print("[WARN] Nu am găsit niciun user de salvat.")

# ------------------- SCRAPING FĂRĂ LOGIN -------------------
import requests
import time

BASE_URL = "https://www.reddit.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}  # Header pentru a evita blocarea request-urilor

def collect_new_users(max_users=100):
    """
    Colectează utilizatori noi de pe Reddit folosind endpoint-ul public /new.json
    Nu necesită autentificare.
    """
    users_data = {}
    after = None  # Folosit pentru paginare

    while len(users_data) < max_users:
        url = f"{BASE_URL}/new.json?limit=100"
        if after:
            url += f"&after={after}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        
        # Iterăm prin postările returnate și extragem autorii
        for child in data["data"]["children"]:
            author = child["data"].get("author")
            if author and author not in users_data:
                users_data[author] = {
                    "reddit_id": child["data"].get("author_fullname"),
                    "name": author,
                    "is_online": False,       # Implicit offline
                    "recent_comments": []     # Va fi completat ulterior
                }
        
        # Pregătim următoarea pagină
        after = data["data"].get("after")
        if not after:
            break

    return users_data

# ------------------- ÎMBOGĂȚIREA DATELOR CU ACTIVITATE -------------------
async def enrich_with_activity(users_data, cookies, headers,
                               batch_size=10,
                               delay_between_requests=3,
                               delay_between_batches=10):
    """
    - Pentru fiecare user din users_data:
    - Ia ultimele 3 comentarii
    - Salvează textul, subreddit-ul și timestamp-ul
    - Marchează userul ca online dacă a comentat în ultima oră
    - Procesează userii în loturi
    - Folosește rotație de proxy-uri (o sesiune per batch)
    - Retry la 429 Too Many Requests
    - Pauze între request-uri și între batch-uri
    """
    now = time.time()
    usernames = list(users_data.keys())

    # Creează sesiunile cu proxy-uri
    session_list = await create_sessions_with_proxies(cookies, headers)
    session_cycle = cycle(session_list)  # pentru rotație

    def batched(iterable, n):
        it = iter(iterable)
        while batch := list(islice(it, n)):
            yield batch

    for batch in batched(usernames, batch_size):
        session = next(session_cycle)  # schimbă sesiunea la fiecare batch
        logger.info(f"🔄 Folosesc un nou proxy/session pentru acest batch ({len(batch)} useri)")

        for username in batch:
            url = f"{BASE_URL}/user/{username}/comments/.json?limit=3"
            logger.info(f"📋 enrich_with_activity {url}")

            try:
                r = await session.get(url, timeout=10)

                if r.status_code == 429:
                    logger.warning(f"[WARN] 429 Too Many Requests pentru {username}, aștept 120 secunde...")
                    time.sleep(120)
                    r = await session.get(url, timeout=120)

                r.raise_for_status()
                data = r.json()
                comments = data.get("data", {}).get("children", [])

                recent_comments = []
                is_online_flag = False

                for c in comments:
                    created = c["data"].get("created_utc", 0)
                    recent_comments.append({
                        "body": c["data"].get("body"),
                        "subreddit": c["data"].get("subreddit"),
                        "created_utc": created
                    })
                    # Dacă a comentat în ultima oră → considerăm că e online
                    if now - created < 3600:
                        is_online_flag = True

                # Actualizăm datele userului
                users_data[username]["recent_comments"] = recent_comments
                users_data[username]["is_online"] = is_online_flag

            except requests.exceptions.RequestException as e:
                logger.warning(f"[WARN] Request failed for {username}: {e}")
            except ValueError as e:
                logger.warning(f"[WARN] JSON decode failed for {username}: {e}")
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error for {username}: {e}")
                continue

            time.sleep(delay_between_requests)

        logger.info(f"⏳ Pauză {delay_between_batches}s între batch-uri...")
        time.sleep(delay_between_batches)

    return users_data

# ------------------- PUNCT DE INTRARE -------------------
if __name__ == "__main__":
    asyncio.run(main())  # Rulează fluxul asincron de login + scraping
