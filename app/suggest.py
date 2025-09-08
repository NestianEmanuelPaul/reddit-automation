# =========================
# Importuri necesare
# =========================
import os
import hashlib  # pentru generarea unui ID unic pe baza user_id + mesaj
import requests  # pentru apeluri HTTP către API-ul Mistral
import random    # pentru generarea scorurilor randomizate
from typing import Dict, List
from pydantic import BaseModel  # pentru validarea datelor de intrare/ieșire
from app.utils.logger import logger  # logger-ul centralizat al aplicației
from colorama import init, Fore, Style  # pentru colorarea logurilor în consolă
import logging
import time  # pentru delay între retry-uri

# =========================
# Configurare log și fișier de mesaje trimise
# =========================
SUGGEST_LOG_FILE = "sent_messages.log"  # fișier în care se salvează mesajele trimise
sent_ids = set()  # set cu ID-uri unice ale mesajelor deja trimise
init(autoreset=True)  # reset automat al culorilor în terminal

# Dacă există fișierul de log, încarcă ID-urile mesajelor deja trimise
if os.path.exists(SUGGEST_LOG_FILE):
    with open(SUGGEST_LOG_FILE, encoding="utf-8") as f:
        for line in f:
            sent_ids.add(line.strip().split("|")[0])

# URL-ul spațiului Mistral (poate fi setat din variabile de mediu)
SPACE_URL = os.getenv("SPACE_URL", "").rstrip("/")

# =========================
# Modele Pydantic pentru request/response
# =========================
class SuggestRequest(BaseModel):
    user_id: str
    features: Dict
    history: List[str]

class Suggestion(BaseModel):
    message: str
    score: float

class SuggestResponse(BaseModel):
    user_id: str
    suggestions: List[Suggestion]

# =========================
# Funcție: unique_id
# =========================
def unique_id(user_id, message):
    """
    Creează un hash SHA-256 unic pentru combinația user_id + mesaj.
    Folosit pentru a evita trimiterea aceluiași mesaj de mai multe ori.
    """
    return hashlib.sha256(f"{user_id}:{message}".encode()).hexdigest()

# =========================
# Configurare API Mistral
# =========================
logger = logging.getLogger(__name__)

API_URL = "https://api.mistral.ai/v1/chat/completions"
API_KEY = "ALiftd20j0mwwGd2LwFl4AJmawufa61B"  # cheia API (ar trebui stocată securizat)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

# =========================
# Funcție: call_mistral_space
# =========================
def call_mistral_space(history, features, max_retries=3, backoff_factor=2):
    """
    Trimite promptul către API-ul Mistral și primește mesaje generate.
    - history: istoricul conversației (listă de string-uri)
    - features: trăsături suplimentare despre utilizator (dict)
    - max_retries: numărul maxim de reîncercări în caz de eroare
    - backoff_factor: factor de multiplicare a delay-ului între reîncercări
    """
    # Construim promptul pentru model
    prompt = (
        f"Generează 2 mesaje scurte și prietenoase "
        f"bazate pe istoricul: {history} și trăsăturile: {features}."
    )

    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    logger.info(f"Payload trimis: {payload}")

    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
            logger.info(f"Status code: {r.status_code}")

            if r.status_code == 200:
                # Încearcă să parseze răspunsul JSON
                try:
                    data = r.json()
                except ValueError:
                    logger.error(f"Răspuns non‑JSON: {r.text!r}")
                    return []

                # Extrage textul generat de model
                try:
                    reply = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError) as e:
                    logger.error(f"Structură de răspuns neașteptată: {e}")
                    return []

                logger.info(f"Raw text: {reply}")

                # Împarte textul în mesaje individuale
                msgs = []
                for line in reply.splitlines():
                    line = line.strip()
                    if line.startswith("*\"") and line.endswith("\"*"):
                        msgs.append(line.strip("*").strip('"'))

                logger.info(f"Mesaje extrase: {msgs}")
                return msgs[:2]  # returnează doar primele 2 mesaje

            elif r.status_code == 429:
                # Too Many Requests → retry cu backoff
                logger.warning(f"Capacitate depășită. Reîncerc în {delay}s (încercarea {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= backoff_factor
                continue
            else:
                logger.error(f"Eroare HTTP {r.status_code}: {r.text!r}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Eroare la apelarea API-ului: {e}")
            return []

    logger.error("Număr maxim de reîncercări atins fără succes.")
    return []

# =========================
# Funcție: suggest_for_user
# =========================
def suggest_for_user(user_id: str, features: Dict, history: List[str]) -> SuggestResponse:
    """
    Trimite datele despre user către modelul Mistral și returnează sugestiile.
    - Loghează fiecare pas cu culori pentru lizibilitate.
    - Evită trimiterea de mesaje duplicate (verifică în sent_ids).
    """
    try:
        # === Log request către model ===
        logger.info(f"{Fore.BLUE}[AI] Trimit către model pentru {user_id}:{Style.RESET_ALL}")
        logger.info(f"{Fore.BLUE}Features: {features}{Style.RESET_ALL}")
        logger.info(f"{Fore.BLUE}History: {history}{Style.RESET_ALL}")

        # === Apel model ===
        messages = call_mistral_space(history, features)

        # === Log răspuns brut ===
        logger.info(f"{Fore.GREEN}[MODEL RAW REPLY pentru {user_id}] {Fore.YELLOW}{messages}{Style.RESET_ALL}")

        suggestions = []
        for m in messages:
            mid = unique_id(user_id, m)
            score = round(random.uniform(0.8, 0.95), 2)  # scor random între 0.8 și 0.95

            # Log sugestie generată
            logger.info(f"{Fore.CYAN}[MODEL→{user_id}]{Style.RESET_ALL} {m} (score={score})")

            # Dacă mesajul nu a mai fost trimis, îl salvăm în fișier și în memorie
            if mid not in sent_ids:
                with open(SUGGEST_LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{mid}|{user_id}|{m}\n")
                sent_ids.add(mid)
                logger.info(f"{Fore.YELLOW}[SENT][{user_id}]{Style.RESET_ALL} {m} (score={score})")

            suggestions.append(Suggestion(message=m, score=score))

        return SuggestResponse(user_id=user_id, suggestions=suggestions)

    except Exception as e:
        logger.error(f"{Fore.RED}[AI] Eroare la generarea sugestiilor pentru {user_id}: {e}{Style.RESET_ALL}")
        return SuggestResponse(user_id=user_id, suggestions=[])



""" def call_mistral_space(history, features):
    Trimite promptul către Space-ul AI și primește mesaje.
    prompt = f"Generează 2 mesaje scurte și prietenoase bazate pe istoricul: {history} și trăsăturile: {features}."
    payload = {
        "user_id": "ai_helper",
        "messages": [{"role": "user", "content": prompt}],
        "force_ro": True
    }
    r = requests.post(f"{SPACE_URL}/chat", json=payload, timeout=60)
    logger.info(f"{r}")
    r.raise_for_status()
    reply = r.json()["reply"]
    logger.info(f"{reply}")
    msgs = [m.strip("-• ").strip() for m in reply.split("\n") if m.strip()]
    logger.info(f"{msgs}")
    return msgs[:2] """

""" def suggest_for_user(user_id: str, features: Dict, history: List[str]) -> SuggestResponse:
    logger.info(f"[DEBUG] Trimit către model pentru {user_id}: features={features}, history={history}")
    messages = call_mistral_space(history, features)
    logger.info(f"{Fore.GREEN}[MODEL RAW REPLY pentru {user_id}] {messages}{Style.RESET_ALL} !!!!!!!!!!!!!")
    suggestions = []
    for m in messages:
        mid = unique_id(user_id, m)
        score = round(random.uniform(0.8, 0.95), 2)
        logger.info(f"[MODEL→{user_id}] {m} (score={score}) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if mid not in sent_ids:
            with open(SUGGEST_LOG_FILE, "a") as f:
                f.write(f"{mid}|{user_id}|{m}\n")
            sent_ids.add(mid)
            logger.info(f"[SENT][{user_id}] {m} (score={score}) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        suggestions.append(Suggestion(message=m, score=score))
    return SuggestResponse(user_id=user_id, suggestions=suggestions) """
