from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from pathlib import Path

# DB path: ./data/app.db (creează folderul dacă nu există)
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_URL = f"sqlite:///{DATA_DIR / 'app.db'}"

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False}  # necesar pentru SQLite în medii non-thread-safe
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def init_db():
    from app.models.user_profile import UserProfile
    from app.models.subreddit_info import SubredditInfo
    Base.metadata.create_all(bind=engine)

# Helper simplu pentru sesiuni
def get_session():
    return SessionLocal()
