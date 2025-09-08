import json
import os
import time
import requests
from playwright.sync_api import Page, BrowserContext
from app.crypto_utils import encrypt_data, decrypt_data
# from settings import REDDIT_USER, REDDIT_PASS, CAPSOLVER_API_KEY

CAPSOLVER_API_KEY = os.getenv("CAPSOLVER_API_KEY")
LOGIN_URL = "https://www.reddit.com/login/?dest=https%3A%2F%2Fwww.reddit.com%2F"

USERNAME = os.getenv("REDDIT_USER")
PASSWORD = os.getenv("REDDIT_PASS")
COOKIES_FILE = "cookies.json"
SESSION_FILE = "session_data.json"

def is_session_valid(session):
    return session and session.get("expires_at", 0) > time.time()

def login():
    # 🔹 Simulare login real — înlocuiește cu API-ul
    print("[INFO] Autentificare...")
    token = "nou_token"
    cookies = {"session_id": "abc123"}
    expires_at = time.time() + 3600
    encrypt_data({
        "token": token,
        "cookies": cookies,
        "expires_at": expires_at
    }, SESSION_FILE)
    return token, cookies

def get_session():
    session = decrypt_data(SESSION_FILE)
    if is_session_valid(session):
        return session["token"], session["cookies"]
    else:
        return login()

# --- Cookie-uri ---
def save_cookies(context: BrowserContext):
    cookies = context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)
    print(f"[OK] Cookie‑urile au fost salvate în {COOKIES_FILE}")

def load_cookies(context: BrowserContext):
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print("[INFO] Cookie‑urile au fost încărcate din fișier.")
        return True
    return False

def cookies_are_valid(page: Page):
    page.goto("https://www.reddit.com/")
    try:
        page.wait_for_selector("a[data-click-id='create_post']", timeout=5000)
        print("[OK] Sesiune validă – login nu este necesar.")
        return True
    except:
        print("[INFO] Cookie‑urile nu mai sunt valide – refac login.")
        return False

def clear_cookies(context: BrowserContext):
    context.clear_cookies()
    try:
        os.remove(COOKIES_FILE)
        print("[INFO] Cookie‑urile locale au fost șterse.")
    except FileNotFoundError:
        pass

# --- Login ---
def ensure_login(context: BrowserContext):
    page = context.new_page()

    # Dacă avem cookie-uri și sunt valide, ieșim
    if load_cookies(context) and cookies_are_valid(page):
        page.close()
        return

    # Curățăm cookie-urile dacă nu sunt valide
    clear_cookies(context)

    print("[INFO] Deschid pagina de login...")
    page.goto(LOGIN_URL)
    page.wait_for_selector('input[name="username"]', timeout=15000)

    """ if check_and_solve_captcha(page):
        print("[INFO] hCaptcha rezolvat înainte de login.") """

    # Tastăm cu delay mic pentru a simula input uman
    page.type('input[name="username"]', USERNAME, delay=100)
    page.type('input[name="password"]', PASSWORD, delay=100)
    time.sleep(0.5)

    # Căutăm butonul în toate cadrele
    selectors = [
        "button[type=submit]",
        "input[type=submit]",
        "button:has-text('Log in')",
        "button:has-text('Sign in')",
        "div[role=button]"
    ]

    def find_and_click():
        for frame in page.frames:
            for sel in selectors:
                try:
                    btn = frame.query_selector(sel)
                    if btn and btn.is_visible():
                        print(f"[OK] Găsit buton cu selectorul: {sel} în frame: {frame.url}")
                        btn.click()
                        return True
                except:
                    pass
        return False

    clicked = False
    for attempt in range(3):
        print(f"[INFO] Încercarea {attempt+1} de click pe buton...")
        if find_and_click():
            clicked = True
            print(f"[OK] Click reușit la încercarea {attempt+1}.")
            break
        else:
            time.sleep(0.5)

    if not clicked:
        print("[WARN] Niciun buton vizibil – trimit formularul cu Enter.")
        page.press('input[name="password"]', 'Enter')

    # Așteptăm puțin și salvăm cookie-urile
    page.wait_for_timeout(5000)
    save_cookies(context)
    page.close()
