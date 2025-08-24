# app/scraper.py
import asyncio
from app.services.auth_service import reddit_login
from app.services.parsing_service import get_recent_users
from app.services.storage_service import upsert_username_list
from app.utils.logger import logger
# from settings import REDDIT_USER, REDDIT_PASS, HF_API_KEY
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("REDDIT_USER")
PASSWORD = os.getenv("REDDIT_PASS")

async def main():
    print("[INFO] Pornim procesul de login...")
    logged_in, session = await reddit_login(USERNAME, PASSWORD)
    if not logged_in:
        print("[EROARE] Login eșuat. Oprire.")
        return

    print("[OK] Login reușit! Începem scraping utilizatori...")
    users = await get_recent_users(session, subreddit="AskReddit", limit=50)
    print(f"[INFO] Am găsit {len(users)} utilizatori.")

    if users:
        upsert_username_list(users)  # aici lista e dict-uri cu reddit_id + câmpuri
        print("[OK] Lista de useri a fost salvată în DB.")
    else:
        print("[WARN] Nu am găsit niciun user de salvat.")

import requests
import time

BASE_URL = "https://www.reddit.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def collect_new_users(max_users=100):
    users_data = {}
    after = None

    while len(users_data) < max_users:
        url = f"{BASE_URL}/new.json?limit=100"
        if after:
            url += f"&after={after}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        
        for child in data["data"]["children"]:
            author = child["data"].get("author")
            if author and author not in users_data:
                users_data[author] = {
                    "reddit_id": child["data"].get("author_fullname"),
                    "name": author,
                    "is_online": False,
                    "recent_comments": []
                }
        
        after = data["data"].get("after")
        if not after:
            break

    return users_data

def enrich_with_activity(users_data):
    # logger.info(f"📋 enrich_with_activity {users_data}")
    now = time.time()
    for username in list(users_data.keys()):
        url = f"{BASE_URL}/user/{username}/comments/.json?limit=3"
        logger.info(f"📋 enrich_with_activity {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            # logger.info(f"📋 enrich_with_activity {r}")

            data = r.json()
            comments = data.get("data", {}).get("children", [])
            # logger.info(f"📋 enrich_with_activity {comments}")

            recent_comments = []
            is_online_flag = False

            for c in comments:
                # logger.info(f"📋 enrich_with_activity {c}")
                created = c["data"].get("created_utc", 0)
                recent_comments.append({
                    "body": c["data"].get("body"),
                    "subreddit": c["data"].get("subreddit"),
                    "created_utc": created
                })
                if now - created < 3600:
                    is_online_flag = True

            users_data[username]["recent_comments"] = recent_comments
            users_data[username]["is_online"] = is_online_flag

        except requests.exceptions.RequestException as e:
            print(f"[WARN] Request failed for {username}: {e}")
        except ValueError as e:
            print(f"[WARN] JSON decode failed for {username}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for {username}: {e}")
            continue
        break

    return users_data


if __name__ == "__main__":
    asyncio.run(main())
