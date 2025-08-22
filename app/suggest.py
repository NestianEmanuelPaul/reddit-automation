import os
import hashlib
import requests
import random
from typing import Dict, List
from pydantic import BaseModel
from app.utils.logger import logger
from colorama import init, Fore, Style
import logging

SUGGEST_LOG_FILE = "sent_messages.log"
sent_ids = set()
init(autoreset=True)

# Încarcă mesaje deja trimise
if os.path.exists(SUGGEST_LOG_FILE):
    with open(SUGGEST_LOG_FILE) as f:
        for line in f:
            sent_ids.add(line.strip().split("|")[0])

SPACE_URL = os.getenv("SPACE_URL", "").rstrip("/")

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

def unique_id(user_id, message):
    return hashlib.sha256(f"{user_id}:{message}".encode()).hexdigest()

logger = logging.getLogger(__name__)

# pentru apel direct mistral
API_URL = "https://api.mistral.ai/v1/chat/completions"
HF_TOKEN = "ALiftd20j0mwwGd2LwFl4AJmawufa61B"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}
payload = {
    "model": "mistral-large-latest",
    "messages": [
        {"role": "user", "content": "Salut! Ce poți face?"}
    ]
}

import time
import requests
import logging

logger = logging.getLogger(__name__)

API_URL = "https://api.mistral.ai/v1/chat/completions"
API_KEY = "ALiftd20j0mwwGd2LwFl4AJmawufa61B"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def call_mistral_space(history, features, max_retries=3, backoff_factor=2):
    """
    Trimite promptul către API-ul Mistral și primește mesaje generate.
    history  -> istoricul conversației (string sau listă)
    features -> trăsături suplimentare (dict)
    """
    # Construim promptul
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
                try:
                    data = r.json()
                except ValueError:
                    logger.error(f"Răspuns non‑JSON: {r.text!r}")
                    return []

                # Extragem conținutul mesajului
                try:
                    reply = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError) as e:
                    logger.error(f"Structură de răspuns neașteptată: {e}")
                    return []

                logger.info(f"Raw text: {reply}")

                # Împărțim în mesaje individuale
                msgs = []
                for line in reply.splitlines():
                    line = line.strip()
                    if line.startswith("*\"") and line.endswith("\"*"):
                        msgs.append(line.strip("*").strip('"'))
                logger.info(f"Mesaje extrase: {msgs}")
                return msgs[:2]

            elif r.status_code == 429:
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

from colorama import Fore, Style
import random

def suggest_for_user(user_id: str, features: Dict, history: List[str]) -> SuggestResponse:
    """
    Trimite datele despre user către modelul Mistral Space și returnează sugestiile.
    Loghează fiecare pas cu culori pentru lizibilitate.
    """
    try:
        # === Log request către model ===
        logger.info(f"{Fore.BLUE}[AI] Trimit către model pentru {user_id}:{Style.RESET_ALL}")
        logger.info(f"{Fore.BLUE}Features: {features}{Style.RESET_ALL}")
        logger.info(f"{Fore.BLUE}History: {history}{Style.RESET_ALL}")

        # === Apel model ===
        messages = call_mistral_space(history, features)

        # === Log răspuns brut ===
        logger.info(f"{Fore.GREEN}[MODEL RAW REPLY pentru {user_id}]{Style.RESET_ALL} {messages}")

        suggestions = []
        for m in messages:
            mid = unique_id(user_id, m)
            score = round(random.uniform(0.8, 0.95), 2)

            # Log sugestie generată
            logger.info(f"{Fore.CYAN}[MODEL→{user_id}]{Style.RESET_ALL} {m} (score={score})")

            # Dacă nu a mai fost trimisă, o salvăm
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

