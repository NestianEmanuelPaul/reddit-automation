import json
import time
import os
import requests
from playwright.sync_api import sync_playwright
# from settings import REDDIT_USER, REDDIT_PASS, CAPSOLVER_API_KEY

CAPSOLVER_API_KEY = "CAP-1BC9D110E8141475BB3809D4B6C6753B"
LOGIN_URL = "https://www.reddit.com/login/?dest=https%3A%2F%2Fwww.reddit.com%2F"

USERNAME = "daniellikescoffee123"
PASSWORD = "RNeixv617fjv6nJ*Yfc+q3k!3R"
COOKIES_FILE = "cookies.json"

def solve_hcaptcha(site_key, url):
    create_task_url = "https://api.capsolver.com/createTask"
    get_result_url = "https://api.capsolver.com/getTaskResult"

    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "HCaptchaTaskProxyless",
            "websiteURL": url,
            "websiteKey": site_key
        }
    }

    print(f"[INFO] Creez task pentru sitekey={site_key} ...")
    create_resp = requests.post(create_task_url, json=payload).json()
    task_id = create_resp.get("taskId")
    if not task_id:
        raise RuntimeError(f"Eroare creare task: {create_resp}")

    while True:
        time.sleep(2)
        resp = requests.post(get_result_url, json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}).json()
        if resp.get("status") == "ready":
            return resp["solution"]["gRecaptchaResponse"]
        elif resp.get("status") == "failed":
            raise RuntimeError(f"Eroare rezolvare captcha: {resp}")

def check_and_solve_captcha(page):
    try:
        element = page.query_selector("iframe[src*='hcaptcha']")
    except:
        element = None

    if element:
        iframe_src = element.get_attribute("src")
        if iframe_src and "sitekey=" in iframe_src:
            site_key = iframe_src.split("sitekey=")[1].split("&")[0]
            print(f"[INFO] Detectat hCaptcha: {site_key}")
            token = solve_hcaptcha(site_key, LOGIN_URL)
            print("[OK] Token primit, îl inserez în formular.")
            page.evaluate("""
                (token) => {
                    let area = document.querySelector('textarea[name="h-captcha-response"]');
                    if (area) { area.value = token; }
                }
            """, token)
            return True
    return False

def save_cookies(page):
    cookies = page.context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)
    print(f"[OK] Cookie‑urile au fost salvate în {COOKIES_FILE}")

def load_cookies(page):
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)
        print("[INFO] Cookie‑urile au fost încărcate din fișier.")
        return True
    return False

def cookies_are_valid(page):
    """Verifică dacă sesiunile încă sunt valide."""
    page.goto("https://www.reddit.com/")
    try:
        # Element prezent doar când ești logat (buton creare postare)
        page.wait_for_selector("a[data-click-id='create_post']", timeout=5000)
        print("[OK] Sesiune validă – login nu este necesar.")
        return True
    except:
        print("[INFO] Cookie‑urile nu mai sunt valide – refac login.")
        return False

def clear_cookies(context):
    context.clear_cookies()
    try:
        os.remove(COOKIES_FILE)
        print("[INFO] Cookie‑urile locale au fost șterse.")
    except FileNotFoundError:
        pass

def ensure_login_form(page, context):
    """Asigură încărcarea reală a formularului, curățând cookie‑urile dacă e nevoie."""
    page.goto(LOGIN_URL)
    try:
        page.wait_for_selector('input[name="username"]', timeout=7000)
        return True
    except:
        # Dacă nu apare formularul, ștergem cookie‑urile și reîncercăm o dată
        print("[WARN] Formularul de login nu a apărut – curăț cookie‑urile și reîncerc.")
        clear_cookies(context)
        page.goto(LOGIN_URL)
        try:
            page.wait_for_selector('input[name="username"]', timeout=7000)
            return True
        except:
            print("[ERROR] Nu pot încărca formularul de login.")
            return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        if load_cookies(page):
            if cookies_are_valid(page):
                time.sleep(5)
                browser.close()
                return
            else:
                clear_cookies(context)

        print("[INFO] Deschid pagina de login...")
        if not ensure_login_form(page, context):
            browser.close()
            return

        if check_and_solve_captcha(page):
            print("[INFO] hCaptcha rezolvat înainte de login.")




        # Tastăm cu delay mic pentru a simula input uman
        page.type('input[name="username"]', USERNAME, delay=100)
        page.type('input[name="password"]', PASSWORD, delay=100)
        time.sleep(0.5)

        # Liste de selectori comuni pentru butonul de submit
        selectors = [
            "button[type=submit]",
            "input[type=submit]",
            "button:has-text('Log in')",
            "button:has-text('Sign in')",
            "div[role=button]"
        ]

        clicked = False

        # Funcție utilitară pentru a căuta în toate cadrele
        def find_and_click():
            for frame in page.frames:
                for sel in selectors:
                    try:
                        btn = frame.query_selector(sel)
                        if btn and btn.is_visible():
                            print(f"[OK] Găsit buton cu selectorul: {sel} în frame: {frame.url}")
                            btn.click()
                            return True
                    except Exception:
                        pass
            return False

        # Încercăm de câteva ori, cu căutare proaspătă
        for attempt in range(3):
            print(f"[INFO] Încercarea {attempt+1} de click pe buton...")
            if find_and_click():
                clicked = True
                print(f"[OK] Click reușit la încercarea {attempt+1}.")
                break
            else:
                time.sleep(0.5)

        # Fallback dacă nu am reușit click
        if not clicked:
            print("[WARN] Niciun buton vizibil – trimit formularul cu Enter.")
            page.press('input[name="password"]', 'Enter')





        page.wait_for_timeout(3000)

        if check_and_solve_captcha(page):
            print("[INFO] hCaptcha rezolvat după submit.")
            try:
                page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=5000)
                page.click('button[type="submit"]')
            except:
                pass

        page.wait_for_timeout(5000)
        save_cookies(page)

        browser.close()

if __name__ == "__main__":
    main()
