from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
def metrics():
    return {
        "logins_total": 0,
        "login_errors_total": 0,
        "scraped_users_total": 0,
        "messages_generated_total": 0
    }
