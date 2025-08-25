Quick Start – Proiect FastAPI + Docker
1️⃣ Cerințe
Docker Desktop instalat și pornit

Python 3.10+ instalat

Fișier .env cu datele de configurare (vezi mai jos)

2️⃣ Configurare .env
Creează un fișier .env în rădăcina proiectului cu:

env
REDDIT_USER=utilizatorul_tau
REDDIT_PASS=parola_ta
CAPSOLVER_API_KEY=cheia_ta_capsolver
TELEGRAM_BOT_TOKEN=tokenul_botului
TELEGRAM_CHAT_ID=id_chat
3️⃣ Pornire servicii din Docker
În folderul proiectului:

bash
docker compose up -d
Acest pas pornește Redis, Kafka și Zookeeper.

4️⃣ Instalare dependențe
bash
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
5️⃣ Pornire aplicație FastAPI
bash
uvicorn main:app --reload
Aplicația: http://127.0.0.1:8000

Documentație API: http://127.0.0.1:8000/docs

6️⃣ Endpoint-uri utile
GET / – test conexiune

GET /health – status aplicație

GET /metrics – statistici

POST /run-orchestration – rulează orchestratorul

POST /suggest – sugestii AI