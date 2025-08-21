# migrate_name_to_reddit_id.py
import asyncio
import httpx
from sqlalchemy import inspect, text
from app.db.database import engine, SessionLocal
from app.models.user_profile import UserProfile
from app.utils.logger import logger

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://www.reddit.com"

def column_exists(table_name, column_name):
    insp = inspect(engine)
    return column_name in [col['name'] for col in insp.get_columns(table_name)]

async def fetch_reddit_id(client: httpx.AsyncClient, username: str) -> str | None:
    """Cere /about.json și returnează reddit_id sau None."""
    url = f"{BASE_URL}/user/{username}/about.json"
    try:
        r = await client.get(url, headers=HEADERS, timeout=10.0)
        r.raise_for_status()
        data = r.json().get("data", {})
        return data.get("id")
    except Exception as e:
        logger.warning(f"⚠️ Eroare la preluarea reddit_id pentru {username}: {e}")
        return None

async def migrate():
    # 1️⃣ Adaugă coloana reddit_id dacă lipsește
    if not column_exists("user_profiles", "reddit_id"):
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE user_profiles ADD COLUMN reddit_id TEXT"))
            conn.commit()
        logger.info("✅ Coloana reddit_id adăugată în user_profiles")

    session = SessionLocal()
    try:
        users = session.query(UserProfile).all()
        logger.info(f"📦 {len(users)} utilizatori găsiți pentru migrare")

        async with httpx.AsyncClient() as client:
            tasks = []
            for user in users:
                if not user.reddit_id and user.name:
                    tasks.append(fetch_reddit_id(client, user.name))
                else:
                    tasks.append(asyncio.sleep(0, result=user.reddit_id))

            reddit_ids = await asyncio.gather(*tasks)

            # Mapăm reddit_id-urile obținute în obiectele existente
            for user, rid in zip(users, reddit_ids):
                if rid:
                    user.reddit_id = rid
                    logger.info(f"🔄 Setat reddit_id pentru {user.name} → {rid}")
                else:
                    logger.warning(f"⚠️ Nu am putut seta reddit_id pentru {user.name}")

        session.commit()
        logger.info("💾 Migrare finalizată cu succes")
    except Exception as e:
        logger.error(f"❌ Eroare la migrare: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(migrate())
