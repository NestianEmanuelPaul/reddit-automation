import redis
import json
from datetime import timedelta
from app.utils.logger import logger
from datetime import datetime, timedelta

# Conectare la Redis (default: localhost:6379)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

REDIS_KEY_PREFIX = "contacted_user:"  # prefix pentru a evita coliziuni
TTL_24H = 86400  # 24 ore în secunde

def filter_online_users(user_dict, max_users=20):
    """
    Returnează până la max_users care:
      1. Sunt online acum SAU activi în ultimele X zile (cutoff)
      2. Dacă nu se umple lista, completează cu utilizatori care au avut vreodată activitate
    Evită utilizatorii contactați în ultimele 24h (TTL_24H în Redis).
    """
    cohort = []
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)  # prag strict

    # --- TREAPTA 1: filtrul strict ---
    for username, data in user_dict.items():
        recent_comments = data.get("recent_comments", [])
        recent_posts = data.get("recent_posts", [])

        active_last_period = any(
            datetime.utcfromtimestamp(c.get("created_utc", 0)) >= cutoff
            for c in recent_posts + recent_comments
        )

        if data.get("is_online") or active_last_period:
            redis_key = f"{REDIS_KEY_PREFIX}{username}"
            if not r.exists(redis_key):
                cohort.append((username, data))
                r.setex(redis_key, TTL_24H, json.dumps(data))

        if len(cohort) >= max_users:
            return dict(cohort)  # lista e plină, nu mai trecem la treapta 2

    # --- TREAPTA 2: completare cu activitate istorică ---
    if len(cohort) < max_users:
        # sortăm după cea mai recentă activitate
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
                continue  # fără activitate istorică

            redis_key = f"{REDIS_KEY_PREFIX}{username}"
            if not r.exists(redis_key):
                cohort.append((username, data))
                r.setex(redis_key, TTL_24H, json.dumps(data))

            if len(cohort) >= max_users:
                break

    return dict(cohort)

def filter_all_users(user_dict, max_users=20):
    cohort = []
    for username, data in user_dict.items():
        cohort.append((username, data))
        if len(cohort) >= max_users:
            break
    return dict(cohort)

