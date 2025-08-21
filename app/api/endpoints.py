from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.models.user_profile import UserProfile
from app.models.subreddit_info import SubredditInfo
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy import func, cast, DateTime

router = APIRouter()

@router.get("/users")
def list_users(
    min_karma: int = 0,
    sort_by: str = "total_karma",
    order: str = "desc",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    query = session.query(UserProfile).filter(UserProfile.total_karma >= min_karma)

    if hasattr(UserProfile, sort_by):
        sort_col = getattr(UserProfile, sort_by)
        query = query.order_by(sort_col.asc() if order.lower() == "asc" else sort_col.desc())

    users = query.offset(offset).limit(limit).all()
    return [
        {
            "name": u.name,
            "total_karma": u.total_karma,
            "comment_karma": u.comment_karma,
            "created_utc": u.created_utc,
            "last_scraped_at": u.last_scraped_at
        }
        for u in users
    ]


@router.get("/subreddits")
def list_subreddits(
    min_subscribers: int = 0,
    sort_by: str = "subscribers",
    order: str = "desc",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    query = session.query(SubredditInfo).filter(SubredditInfo.subscribers >= min_subscribers)

    if hasattr(SubredditInfo, sort_by):
        sort_col = getattr(SubredditInfo, sort_by)
        query = query.order_by(sort_col.asc() if order.lower() == "asc" else sort_col.desc())

    subs = query.offset(offset).limit(limit).all()
    return [
        {
            "name": s.name,
            "subscribers": s.subscribers,
            "active_user_count": s.active_user_count
        }
        for s in subs
    ]


@router.get("/users/cohort")
def cohort_analysis(session: Session = Depends(get_session)):
    results = (
        session.query(
            func.strftime('%Y-%W', cast(UserProfile.created_utc, DateTime)).label('cohort_week'),
            func.count(UserProfile.id).label('user_count'),
            func.avg(UserProfile.total_karma).label('avg_karma')
        )
        .group_by(func.strftime('%Y-%W', cast(UserProfile.created_utc, DateTime)))
        .order_by(func.strftime('%Y-%W', cast(UserProfile.created_utc, DateTime)))
        .all()
    )

    return [
        {
            "cohort_week": r.cohort_week,
            "user_count": r.user_count,
            "avg_karma": float(r.avg_karma)
        }
        for r in results
    ]

