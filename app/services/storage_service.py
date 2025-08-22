from datetime import datetime
from sqlalchemy import select
from app.db.database import get_session, SessionLocal, DB_URL
from app.models.user_profile import UserProfile
from app.models.subreddit_info import SubredditInfo
from app.utils.logger import logger

def upsert_username_list(users_data: list[dict]):
    """
    Upsert în user_profiles pe baza reddit_id.
    Normalizează câmpurile lipsă și face insert/update complet.
    """
    if not users_data:
        logger.info("📭 Lista de utilizatori e goală — nimic de inserat.")
        return

    # Asigură câmpurile obligatorii
    for u in users_data:
        u.setdefault("reddit_id", None)
        u.setdefault("name", None)
        u.setdefault("avatar_url", None)

    session = SessionLocal()
    # logger.info(DB_URL)
    try:
        for user in users_data:
            reddit_id = user["reddit_id"]
            if not reddit_id:
                logger.warning(f"⚠️ Fără reddit_id: {user}")
                continue

            existing = session.execute(
                select(UserProfile).where(UserProfile.reddit_id == reddit_id)
            ).scalar_one_or_none()

            if existing:
                for field, value in user.items():
                    if hasattr(existing, field):
                        setattr(existing, field, value)
                existing.last_scraped_at = datetime.utcnow()
                # logger.info(f"♻️ Update {existing.name} ({reddit_id})")
            else:
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

        session.commit()
        logger.info(f"✅ Upsert efectuat cu succes pentru {len(users_data)} utilizatori.")
    except Exception as e:
        logger.error(f"❌ Eroare la upsert_username_list: {e}")
        session.rollback()
    finally:
        session.close()

def upsert_subreddit_info(profile_data):
    # TODO: implementează logica reală de inserare/actualizare în DB
    print(f"Upserting user: {profile_data}")
