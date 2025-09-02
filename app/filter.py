# =========================
# Importuri necesare
# =========================
import redis  # pentru stocare temporară (cache) și control al rate-limit-ului
import json   # pentru serializarea datelor în Redis
from datetime import datetime, timedelta  # pentru calcule de timp
from app.utils.logger import logger  # logger-ul centralizat al aplicației

# =========================
# Conectare la Redis
# =========================
# Se conectează la un server Redis local (port 6379)
# decode_responses=True → valorile returnate vor fi string-uri, nu bytes
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# =========================
# Constante globale
# =========================
REDIS_KEY_PREFIX = "contacted_user:"  # prefix pentru cheile din Redis (evită coliziuni)
TTL_24H = 86400  # durata de viață a unei chei în secunde (24 ore)

# =========================
# Funcție: filter_online_users
# =========================
def filter_online_users(user_dict, max_users=20):
    """
    Selectează până la max_users utilizatori care:
      1. Sunt online acum SAU au fost activi în ultimele 30 de zile.
      2. Dacă nu se atinge limita, completează cu utilizatori cu activitate istorică.
    Evită utilizatorii contactați în ultimele 24h (prin verificarea în Redis).
    """
    cohort = []  # listă de tuple (username, data)
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)  # prag de activitate recentă

    # --- TREAPTA 1: Filtrare strictă (online sau activ recent) ---
    for username, data in user_dict.items():
        recent_comments = data.get("recent_comments", [])
        recent_posts = data.get("recent_posts", [])

        # Verifică dacă există activitate după cutoff
        active_last_period = any(
            datetime.utcfromtimestamp(c.get("created_utc", 0)) >= cutoff
            for c in recent_posts + recent_comments
        )

        # Dacă utilizatorul e online sau activ recent și nu a fost contactat în ultimele 24h
        if data.get("is_online") or active_last_period:
            redis_key = f"{REDIS_KEY_PREFIX}{username}"
            if not r.exists(redis_key):
                cohort.append((username, data))
                # Salvează în Redis pentru a evita contactarea repetată în 24h
                r.setex(redis_key, TTL_24H, json.dumps(data))

        # Dacă am atins limita, returnăm direct
        if len(cohort) >= max_users:
            return dict(cohort)

    # --- TREAPTA 2: Completare cu utilizatori cu activitate istorică ---
    if len(cohort) < max_users:
        # Sortează utilizatorii după cea mai recentă activitate (post sau comentariu)
        sorted_users = sorted(
            user_dict.items(),
            key=lambda x: max(
                [c.get("created_utc", 0) for c in x[1].get("recent_posts", []) + x[1].get("recent_comments", [])] or [0]
            ),
            reverse=True
        )

        for username, data in sorted_users:
            if (username, data) in cohort:
                continue  # deja inclus
            if not (data.get("recent_posts") or data.get("recent_comments")):
                continue  # fără activitate deloc

            redis_key = f"{REDIS_KEY_PREFIX}{username}"
            if not r.exists(redis_key):
                cohort.append((username, data))
                r.setex(redis_key, TTL_24H, json.dumps(data))

            if len(cohort) >= max_users:
                break

    return dict(cohort)

# =========================
# Funcție: filter_all_users
# =========================
def filter_all_users(user_dict, max_users=20):
    """
    Returnează primii max_users din user_dict, fără filtrare suplimentară.
    Util pentru testare sau cazuri în care nu contează activitatea recentă.
    """
    cohort = []
    for username, data in user_dict.items():
        cohort.append((username, data))
        if len(cohort) >= max_users:
            break
    return dict(cohort)
