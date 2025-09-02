# =========================
# Importuri standard și din aplicație
# =========================
import os
import json
import asyncio
import requests
from playwright.async_api import async_playwright, BrowserContext, Page  # Playwright pentru automatizare browser
from app.utils.logger import logger
from colorama import Fore, Style  # pentru colorarea mesajelor în log

# =========================
# Configurări și constante
# =========================
CAPSOLVER_API_KEY = os.getenv("CAPSOLVER_API_KEY", "CAP-CHANGE-ME")  # cheia API pentru serviciul de rezolvare captcha
LOGIN_URL = "https://www.reddit.com/login/?dest=https%3A%2F%2Fwww.reddit.com%2F"
HOME_URL = "https://www.reddit.com/"
COOKIES_FILE = "cookies.json"  # fișier local pentru salvarea cookie-urilor

# ---------------- hCaptcha ----------------
def _solve_hcaptcha_sync(site_key: str, url: str) -> str:
    """
    Rezolvă un hCaptcha folosind API-ul CapSolver (sincron).
    Creează un task, apoi verifică periodic până primește soluția.
    """
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

    # Creează task-ul de rezolvare captcha
    resp = requests.post(create_task_url, json=payload, timeout=30).json()
    task_id = resp.get("taskId")
    if not task_id:
        raise RuntimeError(f"Eroare creare task CapSolver: {resp}")

    # Așteaptă până când task-ul este rezolvat
    import time
    while True:
        check = requests.post(get_result_url, json={"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}, timeout=30).json()
        if check.get("status") == "ready":
            return check["solution"]["gRecaptchaResponse"]
        if check.get("status") == "failed":
            raise RuntimeError(f"Eroare rezolvare captcha: {check}")
        time.sleep(2)

async def _check_and_solve_captcha(page: Page) -> bool:
    """
    Verifică dacă există un iframe hCaptcha pe pagină și îl rezolvă dacă este găsit.
    """
    iframe = await page.query_selector("iframe[src*='hcaptcha']")
    if not iframe:
        return False
    src = await iframe.get_attribute("src")
    if not src or "sitekey=" not in src:
        return False
    site_key = src.split("sitekey=")[1].split("&")[0]
    logger.info(f"Detectat hCaptcha cu sitekey={site_key}. Rezolv...")
    token = await asyncio.to_thread(_solve_hcaptcha_sync, site_key, LOGIN_URL)
    # Injectează token-ul în pagina curentă
    await page.evaluate(
        """(token) => {
            let area = document.querySelector('textarea[name="h-captcha-response"]');
            if (!area) {
              area = document.createElement('textarea');
              area.name = 'h-captcha-response';
              area.style.display = 'none';
              document.body.appendChild(area);
            }
            area.value = token;
        }""",
        token,
    )
    return True

# ---------------- Cookies ----------------
async def _save_cookies(context: BrowserContext) -> None:
    """
    Salvează cookie-urile din contextul browserului într-un fișier JSON local.
    """
    cookies = await context.cookies()
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f)
    logger.info(f"Cookie-urile au fost salvate în {COOKIES_FILE}")

async def _load_cookies(context: BrowserContext) -> bool:
    """
    Încarcă cookie-urile din fișierul local în contextul browserului.
    Returnează True dacă încărcarea a reușit.
    """
    if not os.path.exists(COOKIES_FILE):
        return False
    try:
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        logger.info("Cookie-urile au fost încărcate din fișier.")
        return True
    except Exception as e:
        logger.warning(f"Nu am putut încărca cookie-urile: {e}")
        return False

async def _cookies_are_valid(page):
    """
    Verifică dacă sesiunea este validă pe baza prezenței unor elemente specifice în UI-ul Reddit.
    """
    try:
        await page.goto("https://www.reddit.com", wait_until="domcontentloaded", timeout=30000)
        login_indicators = [
            "a[data-click-id='create_post']",
            "a[href^='/user/']",
            "header img[alt*='Avatar']"
        ]
        for selector in login_indicators:
            try:
                await page.wait_for_selector(selector, timeout=8000)
                logger.info(f"✅ Sesiune validă — găsit indicator: {selector}")
                return True
            except:
                logger.debug(f"❌ Selectorul {selector} nu a fost găsit încă.")
        logger.warning("⚠️ Niciun indicator de login nu a fost găsit — sesiune invalidă.")
        return False
    except Exception as e:
        logger.warning(f"⚠️ Eroare la verificarea sesiunii: {e}")
        return False

async def _clear_cookies(context: BrowserContext) -> None:
    """
    Șterge cookie-urile din context și din fișierul local.
    """
    await context.clear_cookies()
    try:
        os.remove(COOKIES_FILE)
    except FileNotFoundError:
        pass

# ---------------- Submit login ----------------
async def _try_submit_login(page: Page) -> None:
    """
    Încearcă să apese pe butonul de login folosind mai mulți selectori posibili.
    Dacă nu găsește niciun buton, trimite Enter în câmpul de parolă.
    """
    selectors = [
        "button[type=submit]",
        "input[type=submit]",
        "button:has-text('Log in')",
        "button:has-text('Sign in')"
    ]
    for sel in selectors:
        try:
            await page.click(sel, timeout=1500)
            logger.info(f"Click pe buton cu selectorul: {sel}")
            return
        except:
            continue
    logger.warning("Nu am găsit buton – trimit Enter.")
    await page.press('input[name="password"]', "Enter")

# ---------------- Main login ----------------
async def reddit_login(username: str, password: str, session=None):
    """
    Funcția principală de login pe Reddit:
    - Încearcă să folosească cookie-uri salvate pentru a evita login-ul
    - Dacă nu sunt valide, face login nou cu Playwright
    - Rezolvă hCaptcha dacă apare
    - Salvează cookie-urile pentru sesiuni viitoare
    - Returnează True + sesiunea httpx cu cookie-urile setate
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()

        # Încearcă să încarce cookie-urile salvate
        cookies_loaded = await _load_cookies(context)
        page = await context.new_page()

        if cookies_loaded:
            logger.info(f"🍪 {Fore.GREEN}Cookie-uri încărcate — verific sesiunea...{Style.RESET_ALL}")
            if await _cookies_are_valid(page):
                logger.info(f"✅ {Fore.GREEN}Sesiune validă — login nu este necesar.{Style.RESET_ALL}")
                cookies = await context.cookies()
                await browser.close()
                if session is None:
                    from httpx import AsyncClient
                    session = AsyncClient()
                for c in cookies:
                    session.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path'))
                return True, session
            else:
                logger.info(f"⚠️ {Fore.RED}Cookie-urile nu mai sunt valide — fac login nou.{Style.RESET_ALL}")
                await _clear_cookies(context)

        # Navighează la pagina de login
        logger.info("🌐 Navighez la pagina de login...")
        await page.goto("https://www.reddit.com/login", timeout=60000)

        # Rezolvă hCaptcha dacă apare
        captcha_resolved = await _check_and_solve_captcha(page)
        if captcha_resolved:
            logger.info(f"✅ {Fore.BLUE}hCaptcha rezolvat automat.{Style.RESET_ALL}")
        else:
            logger.info(f"ℹ️ {Fore.BLUE}Nu a apărut hCaptcha la login.{Style.RESET_ALL}")

        # Acceptă cookie banner dacă apare
        try:
            await page.wait_for_selector('button:has-text("Accept all")', timeout=5000)
            await page.click('button:has-text("Accept all")')
            logger.info("🍪 Banner de consimțământ închis")
        except:
            logger.info("🍪 Nu a apărut bannerul de consimțământ")

        # 2. Așteaptă câmpurile de login să fie vizibile
        await page.wait_for_selector('input[name="username"]', timeout=20000)
        await page.wait_for_selector('input[name="password"]', timeout=20000)

        # 3. Completează credențialele
        logger.info("⌨️ Introduc credențialele...")
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)

        # 4. Apasă butonul Log in
        logger.info("🔘 Click pe butonul Log in")
        await page.click("button:has-text('Log in')")

        # Așteaptă max 20s pentru oricare dintre semnele de login reușit
        try:
            await page.wait_for_selector("a[href^='/user/']", timeout=20000)
            logger.info("✅ Login reușit (selector link profil găsit)")
        except:
            try:
                await page.wait_for_selector("header img[alt*='Avatar']", timeout=5000)
                logger.info("✅ Login reușit (avatar găsit)")
            except:
                logger.error("❌ Login nereușit – nu am găsit indicatorul de sesiune activă.")
                await page.screenshot(path="login_failed.png")
                await browser.close()
                return False, None

        # 🔹 Salvăm cookie-urile pentru sesiuni viitoare
        await _save_cookies(context)
        logger.info(f"⚠️ {Fore.BLUE}Cookie-urile sunt salvate din nou.{Style.RESET_ALL}")
                
        cookies = await context.cookies()
        await browser.close()

        # Dacă nu avem sesiune primită, creăm una nouă
        if session is None:
            from httpx import AsyncClient
            session = AsyncClient()

        # Adaugă cookie-urile în sesiunea existentă
        for c in cookies:
            session.cookies.set(
                c['name'],
                c['value'],
                domain=c.get('domain'),
                path=c.get('path')
            )

        return True, session


