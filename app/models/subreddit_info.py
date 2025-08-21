from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.database import Base

class SubredditInfo(Base):
    __tablename__ = "subreddits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reddit_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)

    subscribers: Mapped[int] = mapped_column(Integer, default=0)
    active_user_count: Mapped[int] = mapped_column(Integer, default=0)

    created_utc: Mapped[float] = mapped_column(Float, default=0.0)
    url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(String(8000), nullable=True)

    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
