from fastapi import APIRouter
from app.services.auth_service import reddit_login
from app.services.scrape_service import scrape_user_profile
from app.services.ai_service import generate_message

router = APIRouter()

@router.get("/test-flow/{username}")
async def test_flow(username: str):
    cookies = await reddit_login()
    if not cookies:
        return {"status": "error", "detail": "Login failed"}
    
    profile = await scrape_user_profile(username, cookies)
    if not profile:
        return {"status": "error", "detail": "Scraping failed"}
    
    msg = generate_message(profile.get("data", {}))
    return {"status": "ok", "message": msg}
