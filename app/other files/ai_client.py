import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL_ID = "gpt-oss-20b"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

SYSTEM_PROMPT = (
    "Ești un asistent prietenos, creativ și politicos. "
    "Generează mesaje scurte (1-2 fraze), personalizate, "
    "pe baza contextului și a comentariilor primite. "
    "Folosește ton pozitiv și un limbaj natural, care să sune uman. "
    "Evită formulările generice și repetițiile."
)

def generate_message(comments: str, max_tokens=100, temperature=0.7) -> str:
    prompt = f"<s>[INST] {SYSTEM_PROMPT}\nComentarii:\n{comments} [/INST]"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    # Extrage textul generat corect
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"].replace(prompt, "").strip()

    return str(data)
