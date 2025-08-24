# Reddit Automation Orchestrator

## 📌 Descriere
Acest proiect este un **orchestrator automatizat pentru Reddit**, care:
- Se autentifică pe Reddit folosind **Playwright** și proxy-uri SOCKS5.
- Monitorizează conexiunea la internet și starea sesiunii, cu **relogin automat**.
- Colectează și îmbogățește date despre utilizatori și subreddit-uri.
- Filtrează cohorta de utilizatori și generează sugestii folosind un modul AI.
- Rulează ca aplicație **FastAPI**, cu endpoint-uri pentru orchestrare manuală și sugestii.

---

## 🚀 Funcționalități implementate

### 🔹 Login și sesiuni
- **Login prin Playwright + SOCKS5** (testat și funcțional).
- Rotație automată a proxy-urilor SOCKS5 pentru scraping (`itertools.cycle`).
- Fallback la sesiune fără proxy dacă niciun SOCKS5 nu este valid.
- Citirea credențialelor din `.env` (fără hardcodare în cod).

### 🔹 Monitorizare și reconectare
- Verificare periodică a conexiunii la internet.
- Verificare stării de login.
- Relogin automat dacă apare o problemă.
- Alerte Telegram la reconectare sau erori.

### 🔹 Scraping și AI
- Colectare utilizatori noi (`collect_new_users`).
- Îmbogățire date cu activitate (`enrich_with_activity`).
- Filtrare cohortă (`filter_online_users`, `filter_all_users`).
- Generare sugestii AI (`suggest_for_user`) pentru fiecare utilizator din cohortă.

### 🔹 Organizare cod
- Curățare fișiere de importuri și cod nefolositor.
- Structură modulară propusă:
app/
orchestration/
services/
utils/
db/
routers/
main.py

---

## 📂 Structura proiectului (stadiu actual)

project_root/ 
│ ├── .env 
├── main.py # punct de intrare FastAPI 
├── app/ 
│ ├── orchestration/ 
│ │ └── orchestrator.py 
│ ├── services/ 
│ │ ├── auth_service.py 
│ │ ├── scrape_service.py 
│ │ └── storage_service.py 
│ ├── utils/ 
│ │ ├── logger.py 
│ │ └── proxy_manager.py 
│ ├── routers/ 
│ │ ├── health.py 
│ │ ├── metrics.py 
│ │ └── test_flow.py 
│ ├── db/ 
│ │ └── database.py 
│ ├── ai_client.py 
│ ├── scraper.py 
│ ├── filter.py 
│ └── suggest.py 
└── requirements.txt


---

## ⚙️ Instalare și configurare

### 1. Clonare proiect

git clone <repo-url>
cd reddit-automation

2. Creare mediu virtual și instalare dependențe

python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

3. Configurare .env
Creează fișierul .env în root-ul proiectului (optional):

REDDIT_USER=utilizatorul_tau
REDDIT_PASS=parola_ta
CAPSOLVER_API_KEY=cheia_ta_capsolver
TELEGRAM_BOT_TOKEN=tokenul_botului
TELEGRAM_CHAT_ID=id_chat

4. Configurare config.json
Fișierul config.json conține lista de utilizatori și subreddit-uri țintă:

{
  "users": ["user1", "user2"],
  "subreddits": ["sub1", "sub2"]
}

▶️ Rulare
Pornire server FastAPI

uvicorn main:app --reload

Serverul va fi disponibil la: http://127.0.0.1:8000

Endpoint-uri disponibile
GET / – răspuns simplu de test.

POST /run-orchestration – rulează orchestratorul manual.

POST /suggest – generează sugestii AI pentru un utilizator.

📌 Ce nu este încă implementat
Login HTTP + fallback SOCKS5 – discutat, dar neimplementat.

Integrare completă rezolvare hCaptcha – funcția există, dar nu e apelată în fluxul de login.

Reutilizarea cookie-urilor – funcțiile există, dar nu sunt integrate.

Mutarea completă pe structura modulară propusă – unele endpoint-uri sunt încă în main.py.

Testare automată – nu există teste unitare/integration.

Documentație tehnică detaliată – acest README este primul pas.


⏳ Estimare timp pe sarcini

Sarcină ---> Descriere ---> Ore estimate
1. Implementare login cu Playwright + SOCKS5 ---> Scriere script login, integrare proxy-uri, testare funcțională ---> 7h
2. Gestionare rotație proxy și fallback ---> Implementare itertools.cycle, verificare proxy-uri, fallback la conexiune directă ---> 3h
3. Monitorizare conexiune + relogin automat ---> Verificare periodică internet, status login, reconectare automată ---> 4h
4. Integrare alerte Telegram ---> Configurare bot, trimitere mesaje la erori/relogin ---> 2h
5. Scraping utilizatori și subreddit-uri ---> Funcții collect_new_users, enrich_with_activity ---> 6h
6. Filtrare cohortă ---> Implementare filter_online_users, filter_all_users ---> 2h
7. Generare sugestii AI ---> Integrare modul AI, funcția suggest_for_user ---> 3h
8. Organizare cod și curățare importuri ---> Restructurare fișiere, ștergere cod nefolositor ---> 1h
9. Configurare FastAPI + endpoint-uri ---> Creare main.py, rute pentru orchestrare și sugestii ---> 3h
10. Documentație README + config ---> Scriere README, .env, config.json ---> 1h

📊 Rezumat
Total: 32h

Zone majore de timp: login + proxy (9h), scraping + AI (8h), infrastructură API + monitorizare (7h), restul pe organizare și documentație.