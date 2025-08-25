from fastapi import APIRouter
from colorama import init, Fore, Style
from app.utils.logger import logger

router = APIRouter()

@router.get("/metrics")
def metrics():
    logger.info(f"{Fore.RED}📋 Se încarcă metrics.py{Style.RESET_ALL}")
    return {
        "logins_total": 0,
        "login_errors_total": 0,
        "scraped_users_total": 0,
        "messages_generated_total": 0
    }
