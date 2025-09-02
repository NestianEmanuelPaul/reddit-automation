# =========================
# Importuri necesare
# =========================
from datetime import datetime  # pentru a seta timestamp-ul ultimei actualizări
from sqlalchemy import select  # pentru a construi interogări SQLAlchemy
from app.db.database import get_session, SessionLocal, DB_URL  # conexiune și sesiune DB
from app.models.user_profile import UserProfile  # modelul ORM pentru tabela user_profiles
from app.models.subreddit_info import SubredditInfo  # modelul ORM pentru tabela subreddit_info
from app.utils.logger import logger  # logger-ul centralizat al aplicației

# =========================
# Funcție: upsert_username_list
# =========================
def upsert_username_list(users_data: list[dict]):
    """
    Face un "upsert" (insert sau update) în tabela user_profiles pe baza câmpului reddit_id.
    - Dacă userul există deja (reddit_id găsit), îi actualizează câmpurile.
    - Dacă nu există, îl inserează ca înregistrare nouă.
    - Normalizează câmpurile lipsă (setează valori implicite).
    """
    if not users_data:
        logger.info("📭 Lista de utilizatori e goală — nimic de inserat.")
        return

    # Asigură că fiecare dict din listă are câmpurile obligatorii
    for u in users_data:
        u.setdefault("reddit_id", None)
        u.setdefault("name", None)
        u.setdefault("avatar_url", None)

    # Creează o sesiune DB nouă
    session = SessionLocal()
    # logger.info(DB_URL)  # ar putea fi folosit pentru debugging

    try:
        for user in users_data:
            reddit_id = user["reddit_id"]
            if not reddit_id:
                # Dacă lipsește reddit_id, nu putem identifica unic userul → skip
                logger.warning(f"⚠️ Fără reddit_id: {user}")
                continue

            # Caută în DB dacă există deja un user cu acest reddit_id
            existing = session.execute(
                select(UserProfile).where(UserProfile.reddit_id == reddit_id)
            ).scalar_one_or_none()

            if existing:
                # Dacă există, actualizează câmpurile existente
                for field, value in user.items():
                    if hasattr(existing, field):
                        setattr(existing, field, value)
                # Actualizează timestamp-ul ultimei colectări
                existing.last_scraped_at = datetime.utcnow()
                # logger.info(f"♻️ Update {existing.name} ({reddit_id})")
            else:
                # Dacă nu există, creează un obiect UserProfile nou și îl adaugă în sesiune
                session.add(UserProfile(
                    reddit_id=reddit_id,
                    name=user.get("name"),
                    total_karma=user.get("total_karma", 0),
                    link_karma=user.get("link_karma", 0),
                    comment_karma=user.get("comment_karma", 0),
                    created_utc=user.get("created_utc", 0.0),
                    is_employee=user.get("is_employee", False),
                    is_gold=user.get("is_gold", False),
                    is_mod=user.get("is_mod", False),
                    verified=user.get("verified", False),
                    avatar_url=user.get("avatar_url"),
                    icon_img=user.get("icon_img"),
                    public_description=user.get("public_description"),
                    last_scraped_at=datetime.utcnow()
                ))
                # logger.info(f"💾 Insert {user.get('name')} ({reddit_id})")

        # Confirmă toate modificările în DB
        session.commit()
        logger.info(f"✅ Upsert efectuat cu succes pentru {len(users_data)} utilizatori.")
    except Exception as e:
        # În caz de eroare, loghează și revine la starea anterioară
        logger.error(f"❌ Eroare la upsert_username_list: {e}")
        session.rollback()
    finally:
        # Închide sesiunea DB
        session.close()

# =========================
# Funcție: upsert_subreddit_info
# =========================
def upsert_subreddit_info(profile_data):
    """
    TODO: De implementat logica reală de inserare/actualizare pentru informațiile despre subreddit.
    Momentan doar afișează datele primite.
    """
    print(f"Upserting user: {profile_data}")
