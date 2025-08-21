from sqlalchemy import String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.database import Base
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    reddit_id = Column(String, unique=True, index=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    name = Column(String)
    total_karma = Column(Integer, default=0)
    link_karma = Column(Integer, default=0)
    comment_karma = Column(Integer, default=0)
    created_utc = Column(Float)
    is_employee = Column(Boolean, default=False)
    is_gold = Column(Boolean, default=False)
    is_mod = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    icon_img = Column(String)
    public_description = Column(String)
    last_scraped_at = Column(DateTime)

