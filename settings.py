"""
settings.py
Centralizează citirea și validarea variabilelor de mediu (Secrets în Space-ul privat HF).
Folosește automat .env în dezvoltare locală și variabile injectate ca Secrets în Space.
"""

import os

# Încarcă .env doar dacă nu suntem în Hugging Face Space
if not os.getenv("SPACE_ID"):
    from dotenv import load_dotenv
    load_dotenv()

def env_required(key: str) -> str:
    """
    Citește o variabilă obligatorie din env.
    Dacă lipsește → ridică excepție cu mesaj clar.
    """
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"❌ Lipsă variabilă de mediu necesară: {key}")
    return value

""" # 🔑 Credenziale Reddit
REDDIT_USER = env_required("REDDIT_USER")
REDDIT_PASS = env_required("REDDIT_PASS")

# 🔑 Credenziale Telegram chat bot
TELEGRAM_CHAT_ID = env_required("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = env_required("TELEGRAM_TOKEN")

# 🔑 API Hugging Face / Model
HF_API_KEY = env_required("HF_API_KEY")

# 🌐 Proxy (opțional)
PROXY_URL = os.getenv("PROXY_URL")  # poate lipsi

# 🗄 Conexiune baza de date
DB_URL = env_required("DB_URL")

# 🔐 Alte secrete (ex: cheie JWT)
JWT_SECRET_KEY = env_required("JWT_SECRET_KEY")

# Configuri AI / modele fallback
AI_MODEL_ID = os.getenv("AI_MODEL_ID", "mistralai/Mistral-7B-Instruct")

# Debug info (opțional, doar local)
if not os.getenv("SPACE_ID"):
    print("📦 Config încărcat din .env (mod local).")
    print(f"🔹 User Reddit: {REDDIT_USER}")
    print(f"🔹 Model AI: {AI_MODEL_ID}")
 """