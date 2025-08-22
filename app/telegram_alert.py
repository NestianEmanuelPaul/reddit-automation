import requests
import os
from dotenv import load_dotenv
# from settings import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN

load_dotenv()

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{"8379653048:AAHfC4DasoTYiUsfdNa3CtWorRVKw0wMqQc"}/sendMessage"
    payload = {"chat_id": "5937988338", "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"[ALERT ERROR] {e}")
