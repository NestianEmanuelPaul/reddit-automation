import httpx
import asyncio
import random
from app.utils.logger import logger

# Client HTTP global — îl poți importa și folosi direct
async_client = httpx.AsyncClient(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    follow_redirects=True,   # automat pentru toate cererile
    timeout=15
)

async def fetch_with_retry(
    method: str,
    url: str,
    session: httpx.AsyncClient = None,
    retries: int = 3,
    **kwargs
):
    """
    Efectuează o cerere HTTP cu retry automat.
    - Dacă primește un obiect session (httpx.AsyncClient), îl folosește direct.
    - Dacă nu, creează un client temporar (fără login).
    - Dacă primește `proxy`, îl aplică la request.
    """
    attempt = 0
    last_exception = None

    while attempt < retries:
        try:
            if session and hasattr(session, method.lower()):
                # Folosim sesiunea deja autenticată
                resp = await getattr(session, method.lower())(
                    url,
                    **kwargs
                )
            """ else:
                # Fallback pe client temporar
                async with httpx.AsyncClient(proxies=proxy_dict) as client:
                    resp = await getattr(client, method.lower())(url, **kwargs)

                    logger.info(f"NOUL PROXY ESTE : {proxy_dict}") """

            resp.raise_for_status()

            return resp

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            attempt += 1
            last_exception = e
            logger.warning(
                f"[HTTP RETRY] {method.upper()} {url} — încercarea {attempt}/{retries} a eșuat: {e}"
            )
            await asyncio.sleep(2 * attempt)  # backoff progresiv

    logger.error(
        f"[HTTP ERROR] {method.upper()} {url} — toate încercările au eșuat: {last_exception}"
    )
    raise last_exception

