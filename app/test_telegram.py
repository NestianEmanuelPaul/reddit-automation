import os
import requests
from dotenv import load_dotenv
# from settings import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN

# Încărcăm variabilele din .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Mesajul de test
message = "Salut 👋! Acesta este un mesaj de test trimis prin Python."

# Construim URL-ul API Telegram
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Facem request-ul
response = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": message
})

# Verificăm răspunsul
if response.status_code == 200:
    print("✅ Mesaj trimis cu succes!")
else:
    print(f"⚠️ Eroare: {response.status_code} - {response.text}")
