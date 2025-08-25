# Reddit Automation Orchestrator

## 📌 Descriere
Acest proiect este un **orchestrator automatizat pentru Reddit**, care:
- Se autentifică pe Reddit folosind **Playwright** și proxy-uri SOCKS5.
- Integrare completă rezolvare hCaptcha – funcția e apelată în fluxul de login.
- Monitorizează conexiunea la internet și starea sesiunii, cu **relogin automat**.
- Colectează și îmbogățește date despre utilizatori și subreddit-uri.
- Filtrează cohorta de utilizatori și generează sugestii folosind un modul AI.
- Rulează ca aplicație **FastAPI**, cu endpoint-uri pentru orchestrare manuală și sugestii.

---

## 🚀 Funcționalități implementate

### 🔹 Login și sesiuni
- **Login prin Playwright + SOCKS5** (testat și funcțional).
- Reutilizarea cookie-urilor intre sesiuni.
- Rotație automată a proxy-urilor SOCKS5 pentru scraping (`itertools.cycle`).
- Fallback la sesiune fără proxy dacă niciun SOCKS5 nu este valid.
- Citirea credențialelor din `.env` (fără hardcodare în cod).

### 🔹 Monitorizare și reconectare
- Verificare periodică a conexiunii la internet.
- endpoint-uri : /metrics si /health la : http://127.0.0.1:8000/docs
,http://127.0.0.1:8000/metrics
si, http://127.0.0.1:8000/health, unde se afiseaza informatiile : pentru metrics - returnează niște valori numerice (contori) despre activitatea aplicației: logări, erori, utilizatori procesați, mesaje generate, pentru health - iti spune dacă aplicația este „vie” și cât timp a trecut de când a fost pornită (uptime_seconds).
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


********************************************************


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


********************************************************


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


********************************************************


▶️ Rulare

Pași pentru a avea serviciile în Docker Desktop și a le porni
1️⃣ Instalarea Docker Desktop
Descarcă și instalează Docker Desktop de aici: https://www.docker.com/products/docker-desktop/

După instalare, verifică în terminal:

bash
docker --version
docker compose version
2️⃣ Pregătirea fișierului docker-compose.yml
Proiectul are deja un fișier docker-compose.yml, acesta conține definițiile pentru toate serviciile necesare (Redis, Kafka, Zookeeper etc.).

3️⃣ Cum se rulează fișierul .yml
Deschide un terminal în folderul unde se află docker-compose.yml.

Rulează:

bash
docker compose up -d


Pornire server FastAPI

uvicorn main:app --reload

Serverul va fi disponibil la: http://127.0.0.1:8000

Endpoint-uri disponibile
GET / – răspuns simplu de test.

POST /run-orchestration – rulează orchestratorul manual.

POST /suggest – generează sugestii AI pentru un utilizator.

📌 Ce nu este încă implementat
Login HTTP + fallback SOCKS5 – discutat, dar neimplementat.

Mutarea completă pe structura modulară propusă – unele endpoint-uri sunt încă în main.py.

Testare automată – nu există teste unitare/integration.

Documentație tehnică detaliată – acest README este primul pas.


********************************************************


⏳ Estimare timp pe sarcini

Sarcină ---> Descriere ---> Ore estimate
1. Implementare login cu Playwright + SOCKS5 ---> Scriere script login, integrare proxy-uri, reutilizarea cookie-urilor între sesiuni, rezolvare Captcha, testare funcțională ---> 7h
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


********************************************************


Exemplu de log : 

PS C:\Users\rafae\source\repos\reddit-automation> & C:/Users/rafae/source/repos/reddit-automation/.venv/Scripts/Activate.ps1
(.venv) PS C:\Users\rafae\source\repos\reddit-automation> uvicorn main:app --reload                                                
INFO:     Will watch for changes in these directories: ['C:\\Users\\rafae\\source\\repos\\reddit-automation']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [20884] using WatchFiles
INFO:     Started server process [3048]
INFO:     Waiting for application startup.
🚀 Pornire server și monitor...
INFO:     Application startup complete.
2025-08-25 08:12:22,686 INFO [reddit_automation] 🚀 Pornim orchestratorul Reddit
2025-08-25 08:12:22,686 INFO [reddit_automation] C:\Users\rafae\source\repos\reddit-automation\app\orchestration\config.json
2025-08-25 08:12:24,078 INFO [reddit_automation] [08:12:24] ✅ Monitor OK
2025-08-25 08:12:26,380 INFO [httpx] HTTP Request: GET https://httpbin.org/ip "HTTP/1.1 200 OK"
2025-08-25 08:12:26,386 INFO [reddit_automation] ⚠️ 📋 Avem proxy funcțional — socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661
2025-08-25 08:12:26,387 INFO [reddit_automation] ⚠️ 📋 Login folosind proxy: socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661
2025-08-25 08:12:29,170 INFO [reddit_automation] Cookie-urile au fost încărcate din fișier.
2025-08-25 08:12:29,409 INFO [reddit_automation] 🍪 Cookie-uri încărcate — verific sesiunea...
2025-08-25 08:12:35,497 INFO [reddit_automation] [08:12:35] ✅ Monitor OK
2025-08-25 08:12:41,192 WARNING [reddit_automation] ⚠️ Eroare la verificarea sesiunii: Page.goto: net::ERR_SOCKET_NOT_CONNECTED at  https://www.reddit.com/
Call log:
  - navigating to "https://www.reddit.com/", waiting until "domcontentloaded"

2025-08-25 08:12:41,192 INFO [reddit_automation] ⚠️ Cookie-urile nu mai sunt valide — fac login nou.
2025-08-25 08:12:41,200 INFO [reddit_automation] 🌐 Navighez la pagina de login...
2025-08-25 08:12:42,630 INFO [reddit_automation] ℹ️ Nu a apărut hCaptcha la login.
2025-08-25 08:12:43,059 INFO [reddit_automation] 🍪 Banner de consimțământ închis
2025-08-25 08:12:43,083 INFO [reddit_automation] ⌨️ Introduc credențialele...
2025-08-25 08:12:43,338 INFO [reddit_automation] 🔘 Click pe butonul Log in
2025-08-25 08:12:46,737 INFO [reddit_automation] [08:12:46] ✅ Monitor OK
2025-08-25 08:12:49,845 INFO [reddit_automation] ✅ Login reușit (selector link profil găsit)
2025-08-25 08:12:49,869 INFO [reddit_automation] Cookie-urile au fost salvate în cookies.json
2025-08-25 08:12:49,877 INFO [reddit_automation] ⚠️ Cookie-urile sunt salvate din nou.
2025-08-25 08:12:54,163 INFO [httpx] HTTP Request: GET https://httpbin.org/ip "HTTP/1.1 200 OK"
2025-08-25 08:12:55,888 INFO [reddit_automation] ✅ Sesiune adăugată pentru proxy: socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661
2025-08-25 08:12:57,976 INFO [reddit_automation] [08:12:57] ✅ Monitor OK
2025-08-25 08:12:59,521 INFO [httpx] HTTP Request: GET https://httpbin.org/ip "HTTP/1.1 200 OK"
2025-08-25 08:13:01,139 INFO [reddit_automation] ✅ Sesiune adăugată pentru proxy: socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837
2025-08-25 08:13:01,140 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661
2025-08-25 08:13:03,133 INFO [httpx] HTTP Request: GET https://www.reddit.com/user/spez/about.json "HTTP/1.1 200 OK"
2025-08-25 08:13:03,136 WARNING [reddit_automation] ⚠️ Fără reddit_id: {'kind': 't2', 'data': {'is_employee': True, 'is_friend': Faalse, 'subreddit': {'default_set': True, 'user_is_contributor': False, 'banner_img': 'https://b.thumbs.redditmedia.com/KWeEpVxXOGLoloMbM0IxGt9EiKPXizpwFgcSeWqtpZM.png', 'allowed_media_in_comments': [], 'user_is_banned': False, 'free_form_reports': True, 'community_icon': None, 'show_media': True, 'icon_color': '', 'user_is_muted': None, 'display_name': 'u_spez', 'header_img': None, 'title': 'spez', 'previous_names': [], 'over_18': False, 'icon_size': [256, 256], 'primary_color': '', 'icon_img': 'https://styles.redditmedia.com/t5_3k30p/styles/profileIcon_snoo-nftv2_bmZ0X2VpcDE1NToxMzdfNDY2YTMzMDg4N2JkZjYyZDUzZjk2OGVhODI0NzkzMTUwZjA3NzYyZV8zNTIy_rare_4a74ad4e-f76b-458c-86ce-ed9202163a57-headshot.png?width=256&amp;height=256&amp;crop=256:256,smart&amp;s=fb07ab998bb955877134c19f3c766d71ba7b880e', 'description': '', 'submit_link_label': '', 'header_size': None, 'restrict_posting': True, 'restrict_commenting': False, 'subscribers': 0, 'submit_text_label': '', 'is_default_icon': False, 'link_flair_position': '', 'display_name_prefixed': 'u/spez', 'key_color': '', 'name': 't5_3k30p', 'is_default_banner': False, 'url': '/user/spez/', 'quarantine': False, 'banner_size': [1280, 384], 'user_is_moderator': False, 'accept_followers': True, 'public_description': 'Reddit CEO', 'link_flair_enabled': False, 'disable_contributor_requests': False, 'subreddit_type': 'user', 'user_is_subscriber': False}, 'snoovatar_size': [380, 600], 'awardee_karma': 0, 'id': '1w72', 'verified': True, 'is_gold': True, 'is_mod': True, 'awarder_karma': 0, 'has_verified_email': True, 'icon_img': 'https://styles.redditmedia.com/t5_3k30p/styles/profileIcon_snoo-nftv2_bmZ0X2VpcDE1NToxMzdfNDY2YTMzMDg4N2JkZjYyZDUzZjk2OGVhODI0NzkzMTUwZjA3NzYyZV8zNTIy_rare_4a74ad4e-f76b-458c-86ce-ed9202163a57-headshot.png?width=256&amp;height=256&amp;crop=256:256,smart&amp;s=fb07ab998bb955877134c19f3c766d71ba7b880e', 'hide_from_robots': False, 'link_karma': 179751, 'pref_show_snoovatar': False, 'is_blocked': False, 'total_karma': 932359, 'accept_chats': True, 'name': 'spez', 'created': 1118030400.0, 'created_utc': 1118030400.0, 'snoovatar_img': 'https://i.redd.it/snoovatar/avatars/nftv2_bmZ0X2VpcDE1NToxMzdfNDY2YTMzMDg4N2JkZjYyZDUzZjk2OGVhODI0NzkzMTUwZjA3NzYyZV8zNTIy_rare_4a74ad4e-f76b-458c-86ce-ed9202163a57.png', 'comment_karma': 752608, 'accept_followers': True, 'has_subscribed': True, 'accept_pms': True}, 'reddit_id': None, 'name': None, 'avatar_url': None}
2025-08-25 08:13:03,142 INFO [reddit_automation] ✅ Upsert efectuat cu succes pentru 1 utilizatori.
2025-08-25 08:13:03,143 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837  
2025-08-25 08:13:04,729 INFO [httpx] HTTP Request: GET https://www.reddit.com/user/daniellikescoffee123/about.json "HTTP/1.1 200 OK"
2025-08-25 08:13:04,732 WARNING [reddit_automation] ⚠️ Fără reddit_id: {'kind': 't2', 'data': {'is_employee': False, 'has_visited_nnew_profile': False, 'is_friend': False, 'pref_no_profanity': False, 'has_external_account': False, 'pref_geopopular': '', 'pref_show_trending': True, 'subreddit': {'default_set': True, 'user_is_contributor': False, 'banner_img': '', 'allowed_media_in_comments': [], 'user_is_banned': False, 'free_form_reports': True, 'community_icon': None, 'show_media': True, 'icon_color': '#94B3FF', 'user_is_muted': None, 'display_name': 'u_daniellikescoffee123', 'header_img': None, 'title': 'Daniel Likes Coffee', 'coins': 0, 'previous_names': [], 'over_18': False, 'icon_size': [256, 256], 'primary_color': '', 'icon_img': 'https://www.redditstatic.com/avatars/defaults/v2/avatar_default_6.png', 'description': '', 'submit_link_label': '', 'header_size': None, 'restrict_posting': True, 'restrict_commenting': False, 'subscribers': 0, 'submit_text_label': '', 'is_default_icon': True, 'link_flair_position': '', 'display_name_prefixed': 'u/daniellikescoffee123', 'key_color': '', 'name': 't5_bkb1jm', 'is_default_banner': True, 'url': '/user/daniellikescoffee123/', 'quarantine': False, 'banner_size': None, 'user_is_moderator': True, 'accept_followers': True, 'public_description': 'I love reading fantasy books, long walks on the beach, and slaying dragons.\nSometimes I cook pasta.', 'link_flair_enabled': False, 'disable_contributor_requests': False, 'subreddit_type': 'user', 'user_is_subscriber': False}, 'pref_show_presence': True, 'snoovatar_img': '', 'snoovatar_size': None, 'gold_expiration': None, 'has_gold_subscription': False, 'is_sponsor': False, 'num_friends': 0, 'features': {'modmail_harassment_filter': True, 'mod_service_mute_writes': True, 'promoted_trend_blanks': True, 'show_amp_link': True, 'is_email_permission_required': True, 'mod_awards': True, 'mweb_xpromo_revamp_v3': {'owner': 'growth', 'variant': 'control_1', 'experiment_id': 480}, 'mweb_xpromo_revamp_v2': {'owner': 'growth', 'variant': 'control_2', 'experiment_id': 457}, 'awards_on_streams': True, 'mweb_xpromo_modal_listing_click_daily_dismissible_ios': True, 'chat_subreddit': True, 'cookie_consent_banner': True, 'modlog_copyright_removal': True, 'do_not_track': True, 'images_in_comments': True, 'mod_service_mute_reads': True, 'chat_user_settings': True, 'use_pref_account_deployment': True, 'mweb_xpromo_interstitial_comments_ios': True, 'mweb_xpromo_modal_listing_click_daily_dismissible_android': True, 'premium_subscriptions_table': True, 'mweb_xpromo_interstitial_comments_android': True, 'crowd_control_for_post': True, 'mweb_nsfw_xpromo': {'owner': 'growth', 'variant': 'control_2', 'experiment_id': 361}, 'mweb_sharing_web_share_api': {'owner': 'growth', 'variant': 'control_2', 'experiment_id': 314}, 'chat_group_rollout': True, 'resized_styles_images': True, 'noreferrer_to_noopener': True, 'expensive_coins_package': True}, 'can_edit_name': False, 'is_blocked': False, 'verified': True, 'new_modmail_exists': None, 'pref_autoplay': True, 'coins': 0, 'has_paypal_subscription': False, 'has_subscribed_to_premium': False, 'id': '8gs4z7dqm', 'can_create_subreddit': True, 'over_18': True, 'is_gold': False, 'is_mod': False, 'awarder_karma': 0, 'suspension_expiration_utc': None, 'has_stripe_subscription': False, 'is_suspended': False, 'pref_video_autoplay': True, 'has_android_subscription': False, 'in_redesign_beta': True, 'icon_img': 'https://www.redditstatic.com/avatars/defaults/v2/avatar_default_6.png', 'has_mod_mail': False, 'pref_nightmode': True, 'awardee_karma': 0, 'hide_from_robots': False, 'password_set': True, 'modhash': 'gt6j4hwc4aca4a619bb4e2eab7052de60b8736a68416a9ba56', 'link_karma': 1, 'force_password_reset': False, 'total_karma': 1, 'inbox_count': 1, 'pref_top_karma_subreddits': True, 'has_mail': True, 'pref_show_snoovatar': False, 'name': 'daniellikescoffee123', 'pref_clickgadget': 5, 'created': 1716214982.0, 'has_verified_email': False, 'gold_creddits': 0, 'created_utc': 1716214982.0, 'has_ios_subscription': False, 'pref_show_twitter': False, 'in_beta': False, 'comment_karma': 0, 'accept_followers': True, 'has_subscribed': True}, 'reddit_id': None, 'name': None, 'avatar_url': None}
2025-08-25 08:13:04,734 INFO [reddit_automation] ✅ Upsert efectuat cu succes pentru 1 utilizatori.
2025-08-25 08:13:04,734 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661   
2025-08-25 08:13:05,130 INFO [httpx] HTTP Request: GET https://www.reddit.com/user/Emanuel2010Romania/about.json "HTTP/1.1 404 Not Found"
2025-08-25 08:13:05,131 WARNING [reddit_automation] [HTTP RETRY] GET https://www.reddit.com/user/Emanuel2010Romania/about.json — încercarea 1/3 a eșuat: Client error '404 Not Found' for url 'https://www.reddit.com/user/Emanuel2010Romania/about.json'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
2025-08-25 08:13:07,524 INFO [httpx] HTTP Request: GET https://www.reddit.com/user/Emanuel2010Romania/about.json "HTTP/1.1 404 Not Found"
2025-08-25 08:13:07,526 WARNING [reddit_automation] [HTTP RETRY] GET https://www.reddit.com/user/Emanuel2010Romania/about.json — încercarea 2/3 a eșuat: Client error '404 Not Found' for url 'https://www.reddit.com/user/Emanuel2010Romania/about.json'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
2025-08-25 08:13:09,105 INFO [reddit_automation] [08:13:09] ✅ Monitor OK
2025-08-25 08:13:12,125 INFO [httpx] HTTP Request: GET https://www.reddit.com/user/Emanuel2010Romania/about.json "HTTP/1.1 404 Not Found"
2025-08-25 08:13:12,127 WARNING [reddit_automation] [HTTP RETRY] GET https://www.reddit.com/user/Emanuel2010Romania/about.json — încercarea 3/3 a eșuat: Client error '404 Not Found' for url 'https://www.reddit.com/user/Emanuel2010Romania/about.json'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
2025-08-25 08:13:18,138 ERROR [reddit_automation] [HTTP ERROR] GET https://www.reddit.com/user/Emanuel2010Romania/about.json — toate încercările au eșuat: Client error '404 Not Found' for url 'https://www.reddit.com/user/Emanuel2010Romania/about.json'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
2025-08-25 08:13:18,139 ERROR [reddit_automation] Eroare la scraping pentru Emanuel2010Romania: HTTPStatusError -> Client error '404 Not Found' for url 'https://www.reddit.com/user/Emanuel2010Romania/about.json'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
2025-08-25 08:13:18,140 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837  
2025-08-25 08:13:19,810 INFO [httpx] HTTP Request: GET https://www.reddit.com/r/Python/about.json "HTTP/1.1 200 OK"
2025-08-25 08:13:19,826 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661
2025-08-25 08:13:20,400 INFO [reddit_automation] [08:13:20] ✅ Monitor OK
2025-08-25 08:13:21,516 INFO [httpx] HTTP Request: GET https://www.reddit.com/r/learnprogramming/about.json "HTTP/1.1 200 OK"
2025-08-25 08:13:21,518 INFO [reddit_automation] 📋 [Scraping] Folosesc proxy: socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837
2025-08-25 08:13:21,989 INFO [httpx] HTTP Request: GET https://www.reddit.com/r/FastAPI/about.json "HTTP/1.1 200 OK"
2025-08-25 08:13:21,990 INFO [reddit_automation] 🏁 Orchestrator finalizat cu succes
2025-08-25 08:13:31,696 INFO [reddit_automation] [08:13:31] ✅ Monitor OK
2025-08-25 08:13:38,818 INFO [reddit_automation] 📋 Am găsit 191 useri noi
2025-08-25 08:13:38,819 INFO [reddit_automation] [DEBUG] Pornesc enrich_with_activity pentru 191 useri
2025-08-25 08:13:38,819 INFO [reddit_automation] 📋 enrich_with_activity https://www.reddit.com/user/Unuser_/comments/.json?limit=3
2025-08-25 08:13:40,386 INFO [reddit_automation] 📋 Am îmbogățit datele pentru 191 useri
2025-08-25 08:13:40,409 INFO [reddit_automation] 📋 Cohorta finală (20 useri):
2025-08-25 08:13:40,409 INFO [reddit_automation] - Unuser_ | Online: False
2025-08-25 08:13:40,409 INFO [app.suggest] [AI] Trimit către model pentru Unuser_:
2025-08-25 08:13:40,409 INFO [app.suggest] Features: {'karma': 0, 'joined_days': 0}
2025-08-25 08:13:40,410 INFO [app.suggest] History: []
2025-08-25 08:13:40,410 INFO [app.suggest] Payload trimis: {'model': 'mistral-large-latest', 'messages': [{'role': 'user', 'content': "Generează 2 mesaje scurte și prietenoase bazate pe istoricul: [] și trăsăturile: {'karma': 0, 'joined_days': 0}."}]}
2025-08-25 08:13:41,625 INFO [app.suggest] Status code: 429
2025-08-25 08:13:41,626 WARNING [app.suggest] Capacitate depășită. Reîncerc în 1s (încercarea 1/3)
2025-08-25 08:13:42,933 INFO [reddit_automation] [08:13:42] ✅ Monitor OK
2025-08-25 08:13:51,117 INFO [app.suggest] Status code: 200
2025-08-25 08:13:51,118 INFO [app.suggest] Raw text: Deoarece istoricul și trăsăturile indică un utilizator nou (abia s-a alăturat și nu are încă activitate), mesajele vor fi de bun venit, prietenoase și încurajatoare. Iată două variante:

---

**1. Mesaj cald și deschis:**
*"Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨"*

---

**2. Mesaj motivațional și simplu:**
*"Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀"*

---
**Notă:** Am evitat referiri la "karmă" (deoarece este 0) și am accentuat **primire**, **curiozitate** și **sprijin** pentru a crea o primă impresie pozitivă. Dorești ajustări pentru un ton specific (ex. mai umoristic, mai formal)?
2025-08-25 08:13:51,120 INFO [app.suggest] Mesaje extrase: ['Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨', 'Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀']
2025-08-25 08:13:51,122 INFO [app.suggest] [MODEL RAW REPLY pentru Unuser_] ['Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨', 'Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀']
2025-08-25 08:13:51,123 INFO [app.suggest] [MODEL→Unuser_] Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨ (score=0.85)
2025-08-25 08:13:51,129 INFO [app.suggest] [SENT][Unuser_] Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨ (score=0.85)
2025-08-25 08:13:51,129 INFO [app.suggest] [MODEL→Unuser_] Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀 (score=0.85) 
2025-08-25 08:13:51,135 INFO [app.suggest] [SENT][Unuser_] Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀 (score=0.85) 
2025-08-25 08:13:51,138 INFO [reddit_automation] [AI->Unuser_] Bun venit în comunitatea noastră! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează în voie, pune întrebări și nu ezita să te implici – fiecare voce contează! 💬✨ (score=0.85)
2025-08-25 08:13:51,138 INFO [reddit_automation] [AI->Unuser_] Salut și bine ai venit! 👋 Ești nou aici, așa că ia-ți timp să te obișnuiești. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici pentru tine. Succeese frumoase în continuare! 🚀 (score=0.85)
2025-08-25 08:13:51,139 INFO [reddit_automation] - vale_69777 | Online: False
2025-08-25 08:13:51,139 INFO [app.suggest] [AI] Trimit către model pentru vale_69777:
2025-08-25 08:13:51,139 INFO [app.suggest] Features: {'karma': 0, 'joined_days': 0}
2025-08-25 08:13:51,139 INFO [app.suggest] History: []
2025-08-25 08:13:51,140 INFO [app.suggest] Payload trimis: {'model': 'mistral-large-latest', 'messages': [{'role': 'user', 'content': "Generează 2 mesaje scurte și prietenoase bazate pe istoricul: [] și trăsăturile: {'karma': 0, 'joined_days': 0}."}]}
2025-08-25 08:13:52,565 INFO [app.suggest] Status code: 429
2025-08-25 08:13:52,565 WARNING [app.suggest] Capacitate depășită. Reîncerc în 1s (încercarea 1/3)
.........

2025-08-25 08:16:05,174 INFO [app.suggest] Raw text: Deoarece istoricul și trăsăturile indică un utilizator nou (abia s-a alăturat și nu are încă activitate), mesajele vor fi de bun venit, calde și încurajatoare. Iată două variante:

---

**1. (Entuziast și deschis)**
*"Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi?"*

---

**2. (Relaxat și prietenos)**
*"Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături!"*

---
**Notă:** Am evitat referiri la "karmă" (deoarece e 0) și am accentuat **includerea** și **libertatea de a explora** pentru a reduce presiunea asupra unui utilizator începător. Tonul e **pozitiv, deschis și non-intruziv**. Dorești ajustări? 😊
2025-08-25 08:16:05,176 INFO [app.suggest] Mesaje extrase: ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi?', 'Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături!']
2025-08-25 08:16:05,179 INFO [app.suggest] [MODEL RAW REPLY pentru StatusEnd2816] ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi?', 'Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături!']
2025-08-25 08:16:05,180 INFO [app.suggest] [MODEL→StatusEnd2816] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi? (score=0.82)
2025-08-25 08:16:05,185 INFO [app.suggest] [SENT][StatusEnd2816] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi? (score=0.82)
2025-08-25 08:16:05,187 INFO [app.suggest] [MODEL→StatusEnd2816] Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături! (score=0.86)
2025-08-25 08:16:05,206 INFO [app.suggest] [SENT][StatusEnd2816] Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături! (score=0.86)
2025-08-25 08:16:05,211 INFO [reddit_automation] [AI->StatusEnd2816] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Dacă ai întrebări, curiozități sau pur și simplu vrei să spui *bună*, nu ezita – suntem aici să te ajutăm. Ce te-a adus la noi? (score=0.82)
2025-08-25 08:16:05,214 INFO [reddit_automation] [AI->StatusEnd2816] Hei, nou venit! 👋 Nu prea știi încă cum stau lucrurile aici, dar nici noi nu te cunoaștem… așa că hai să remediem asta! Spune-ne ceva despre tine sau pur și simplu explorează în ritmul tău. E frumos să te avem alături! (score=0.86)
2025-08-25 08:16:05,214 INFO [reddit_automation] - Zexification | Online: False
2025-08-25 08:16:05,214 INFO [app.suggest] [AI] Trimit către model pentru Zexification:
2025-08-25 08:16:05,214 INFO [app.suggest] Features: {'karma': 0, 'joined_days': 0}
2025-08-25 08:16:05,215 INFO [app.suggest] History: []
2025-08-25 08:16:05,215 INFO [app.suggest] Payload trimis: {'model': 'mistral-large-latest', 'messages': [{'role': 'user', 'content': "Generează 2 mesaje scurte și prietenoase bazate pe istoricul: [] și trăsăturile: {'karma': 0, 'joined_days': 0}."}]}
2025-08-25 08:16:10,180 INFO [reddit_automation] [08:16:10] ✅ Monitor OK
2025-08-25 08:16:12,173 INFO [app.suggest] Status code: 200
2025-08-25 08:16:12,174 INFO [app.suggest] Raw text: Deoarece istoricul și trăsăturile indică un utilizator nou (abia s-a alăturat și nu are încă activitate), mesajele vor fi de bun venit, încurajatoare și neutre din punct de vedere al karma-ului. Iată două variante:

---

**1. Mesaj cald și deschis:**
*"Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici?"*

---

**2. Mesaj motivațional și simplu:**
*"Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată?"*

---
**Note:**
- Am evitat referiri la karma (pentru că e 0 și ar putea părea neprietenos).
- Am folosit emoji-uri pentru un ton prietenos și deschis.
- Am inclus întrebări deschise pentru a încuraja interacțiunea.
2025-08-25 08:16:12,178 INFO [app.suggest] Mesaje extrase: ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici?', 'Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată?']
2025-08-25 08:16:12,184 INFO [app.suggest] [MODEL RAW REPLY pentru Zexification] ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici?', 'Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată?']
2025-08-25 08:16:12,191 INFO [app.suggest] [MODEL→Zexification] Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici? (score=0.83)
2025-08-25 08:16:12,207 INFO [app.suggest] [SENT][Zexification] Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici? (score=0.83)
2025-08-25 08:16:12,208 INFO [app.suggest] [MODEL→Zexification] Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată? (score=0.85)
2025-08-25 08:16:12,216 INFO [app.suggest] [SENT][Zexification] Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată? (score=0.85)
2025-08-25 08:16:12,216 INFO [reddit_automation] [AI->Zexification] Bun venit în comunitate! 🌟 Abia ai ajuns, dar suntem bucuroși să te avem aici. Orice întrebare sau idee ai avea, nu ezita să o împărtășești – toți am început de undeva. 😊 Ce te-a adus pe aici? (score=0.83)
2025-08-25 08:16:12,220 INFO [reddit_automation] [AI->Zexification] Salut și bine ai venit! 🎉 Ești nou aici, așa că ia-ți timp să explorezi și să te simți ca acasă. Dacă ai nevoie de ajutor sau vrei să socializezi, suntem aici. Ce ți-ar plăcea să descoperi prima dată? (score=0.85)
2025-08-25 08:16:12,221 INFO [reddit_automation] - Relevant-Ad-7639 | Online: False
2025-08-25 08:16:12,222 INFO [app.suggest] [AI] Trimit către model pentru Relevant-Ad-7639:
2025-08-25 08:16:12,223 INFO [app.suggest] Features: {'karma': 0, 'joined_days': 0}
2025-08-25 08:16:12,223 INFO [app.suggest] History: []
2025-08-25 08:16:12,224 INFO [app.suggest] Payload trimis: {'model': 'mistral-large-latest', 'messages': [{'role': 'user', 'content': "Generează 2 mesaje scurte și prietenoase bazate pe istoricul: [] și trăsăturile: {'karma': 0, 'joined_days': 0}."}]}
2025-08-25 08:16:21,340 INFO [reddit_automation] [08:16:21] ✅ Monitor OK
.......

2025-08-25 08:16:41,774 INFO [app.suggest] Raw text: Deoarece istoricul și trăsăturile indică un utilizator nou (abia s-a alăturat și nu are încă activitate), mesajele vor fi de bun venit, calde și încurajatoare. Iată două variante:

---

**1. Mesaj optimist și deschis:**
*"Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi?"*

---

**2. Mesaj simplu și prietenos:**
*"Hei! 👋 Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber?"*

---
**De ce aceste mesaje?**
- **Tonalitate caldă** pentru a reduce eventuala reținere a unui nou venit.
- **Întrebări deschise** pentru a încuraja interacțiunea (fără presiune).
- **Emoji-uri** pentru un ton prietenos și accesibil.
- **Evidențierea oportunităților** (explorare, ajutor, socializare) fără a presupune că utilizatorul știe deja cum funcționează platforma.

Dacă dorești un anumit context (ex: platformă de gaming, rețea profesională etc.), pot adapta mesajele!
2025-08-25 08:16:41,776 INFO [app.suggest] Mesaje extrase: ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi?', 'Hei! �  Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber?']
2025-08-25 08:16:41,778 INFO [app.suggest] [MODEL RAW REPLY pentru Relevant-Ad-7639] ['Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi?', 'Hei! 👋 Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber?']
2025-08-25 08:16:41,778 INFO [app.suggest] [MODEL→Relevant-Ad-7639] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi? (score=0.91)
2025-08-25 08:16:41,786 INFO [app.suggest] [SENT][Relevant-Ad-7639] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi? (score=0.91)
2025-08-25 08:16:41,790 INFO [app.suggest] [MODEL→Relevant-Ad-7639] Hei! 👋 Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber? (score=0.84)  
2025-08-25 08:16:41,795 INFO [app.suggest] [SENT][Relevant-Ad-7639] Hei! 👋 Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber? (score=0.84)  
2025-08-25 08:16:41,795 INFO [reddit_automation] [AI->Relevant-Ad-7639] Bun venit în comunitate! 🌟 Abia ai ajuns, dar deja ne bucurăm că ești aici. Explorează, pune întrebări și nu ezita să te implici – fiecare început este o șansă minunată. Ce te-a adus la noi? (score=0.91)
2025-08-25 08:16:41,796 INFO [reddit_automation] [AI->Relevant-Ad-7639] Hei! 👋 Suntem încântați să te avem alături. Chiar dacă ești nou, aici găsești oameni gata să te ajute sau să schimbe o vorba bună. Spune-ne: ce îți place să faci în timpul liber? (score=0.84)
2025-08-25 08:16:41,797 INFO [reddit_automation] - AmberLeeFMe | Online: False
2025-08-25 08:16:41,797 INFO [app.suggest] [AI] Trimit către model pentru AmberLeeFMe:
2025-08-25 08:16:41,797 INFO [app.suggest] Features: {'karma': 0, 'joined_days': 0}
2025-08-25 08:16:41,797 INFO [app.suggest] History: []
2025-08-25 08:16:41,798 INFO [app.suggest] Payload trimis: {'model': 'mistral-large-latest', 'messages': [{'role': 'user', 'content': "Generează 2 mesaje scurte și prietenoase bazate pe istoricul: [] și trăsăturile: {'karma': 0, 'joined_days': 0}."}]}
2025-08-25 08:16:43,842 INFO [reddit_automation] [08:16:43] ✅ Monitor OK
2025-08-25 08:16:49,424 INFO [app.suggest] Status code: 200
2025-08-25 08:16:49,425 INFO [app.suggest] Raw text: Deoarece istoricul și karma sunt goale, iar utilizatorul este nou (abia s-a înregistrat), mesajele vor fi de bun venit, încurajatoare și neutre. Iată două exemple:

1. **Mesaj 1 (călăuzitor):**
   *"Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊"*

2. **Mesaj 2 (motivațional):**
   *"Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi?"*

**Tonul:** prietenos, deschis și fără presiune, pentru a-l face pe utilizator să se simtă confortabil. 😊
2025-08-25 08:16:49,427 INFO [app.suggest] Mesaje extrase: ['Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊', 'Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi?']
2025-08-25 08:16:49,433 INFO [app.suggest] [MODEL RAW REPLY pentru AmberLeeFMe] ['Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊', 'Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi?']
2025-08-25 08:16:49,435 INFO [app.suggest] [MODEL→AmberLeeFMe] Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊 (score=0.93)
2025-08-25 08:16:49,455 INFO [app.suggest] [SENT][AmberLeeFMe] Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊 (score=0.93)
2025-08-25 08:16:49,457 INFO [app.suggest] [MODEL→AmberLeeFMe] Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi? (score=0.81)
2025-08-25 08:16:49,466 INFO [app.suggest] [SENT][AmberLeeFMe] Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi? (score=0.81)
2025-08-25 08:16:49,467 INFO [reddit_automation] [AI->AmberLeeFMe] Bine ai venit! 🌟 Abia te-ai alăturat comunității, așa că ia-ți timp să explorezi și să descoperi ce ți se potrivește. Orice întrebare ai avea, suntem aici să te ajutăm! 😊 (score=0.93)
2025-08-25 08:16:49,468 INFO [reddit_automation] [AI->AmberLeeFMe] Primul pas e făcut – acum e rândul aventurii! 🚀 Fie că vrei să înveți, să împărtășești sau doar să socializezi, aici e locul potrivit. Ce te-a adus la noi? (score=0.81)
2025-08-25 08:16:55,225 INFO [reddit_automation] [08:16:55] ✅ Monitor OK
