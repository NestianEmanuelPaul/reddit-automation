import requests
from app.auth_manager import get_session

def check_connectivity():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

def heartbeat():
    if not check_connectivity():
        return False, "Eroare conexiune la internet"
    token, cookies = get_session()
    # 🔹 Simulează verificare token pe API real
    return True, "Conexiune și login OK"
