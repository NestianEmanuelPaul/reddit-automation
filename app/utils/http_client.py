# =========================
# Importuri necesare
# =========================
import httpx       # client HTTP asincron și sincron
import asyncio     # pentru sleep asincron (backoff între retry-uri)
import random      # (momentan nefolosit, dar poate fi util pentru randomizare proxy-uri sau delay-uri)
from app.utils.logger import logger  # logger-ul centralizat al aplicației

# =========================
# Client HTTP global
# =========================
# Acest client poate fi importat și folosit direct în alte module.
# Avantaj: păstrează conexiunile deschise (connection pooling) și setările comune.
async_client = httpx.AsyncClient(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},  # header implicit pentru toate cererile
    follow_redirects=True,   # urmează automat redirect-urile HTTP
    timeout=15               # timeout global de 15 secunde
)

# =========================
# Funcție: fetch_with_retry
# =========================
async def fetch_with_retry(
    method: str,
    url: str,
    session: httpx.AsyncClient = None,
    retries: int = 3,
    **kwargs
):
    """
    Efectuează o cerere HTTP cu retry automat.

    Parametri:
      - method: metoda HTTP ("GET", "POST", etc.)
      - url: adresa completă a resursei
      - session: opțional, un obiect httpx.AsyncClient deja configurat (ex: cu autentificare)
      - retries: numărul maxim de încercări în caz de eroare
      - **kwargs: parametri suplimentari pentru request (ex: params, data, json, headers)

    Comportament:
      - Dacă primește un obiect session valid, îl folosește direct.
      - Dacă nu, ar putea crea un client temporar (cod comentat momentan).
      - În caz de eroare de rețea sau status HTTP invalid, reîncearcă cu backoff progresiv.
    """
    attempt = 0
    last_exception = None

    while attempt < retries:
        try:
            if session and hasattr(session, method.lower()):
                # Folosește sesiunea existentă (autentificată sau cu setări speciale)
                resp = await getattr(session, method.lower())(
                    url,
                    **kwargs
                )

            """
            else:
                # Cod comentat: fallback pe client temporar cu proxy
                async with httpx.AsyncClient(proxies=proxy_dict) as client:
                    resp = await getattr(client, method.lower())(url, **kwargs)
                    logger.info(f"NOUL PROXY ESTE : {proxy_dict}")
            """

            # Aruncă excepție dacă status_code nu este 2xx
            resp.raise_for_status()

            # Dacă totul e OK, returnează răspunsul
            return resp

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Crește contorul de încercări și salvează ultima excepție
            attempt += 1
            last_exception = e

            # Loghează avertisment cu detalii despre încercare
            logger.warning(
                f"[HTTP RETRY] {method.upper()} {url} — încercarea {attempt}/{retries} a eșuat: {e}"
            )

            # Așteaptă un timp progresiv înainte de retry (2s, 4s, 6s...)
            await asyncio.sleep(2 * attempt)

    # Dacă toate încercările au eșuat, loghează eroarea și ridică ultima excepție
    logger.error(
        f"[HTTP ERROR] {method.upper()} {url} — toate încercările au eșuat: {last_exception}"
    )
    raise last_exception
