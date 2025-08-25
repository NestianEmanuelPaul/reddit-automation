from fastapi import APIRouter
import time
from colorama import init, Fore, Style
from app.utils.logger import logger

router = APIRouter()

start_time = time.time()

@router.get("/health")
def health_check():
    uptime = round(time.time() - start_time, 2)
    logger.info(f"{Fore.RED}📋 Se încarcă health.py{Style.RESET_ALL}")
    return {"status": "ok", "uptime_seconds": uptime}
