import redis
import json
from datetime import timedelta

# Conectare la Redis (default: localhost:6379)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

REDIS_KEY_PREFIX = "contacted_user:"  # prefix pentru a evita coliziuni
TTL_24H = 86400  # secunde

def filter_online_users(user_dict, max_users=20):
    """
    user_dict: dict cu {username: {...fields...}}
    Returnează max max_users online și necontactați în ultimele 24h.
    """
    cohort = []
    for username, data in user_dict.items():
        if data.get("is_online"):
            redis_key = f"{REDIS_KEY_PREFIX}{username}"
            if not r.exists(redis_key):  # nu a fost contactat recent
                cohort.append((username, data))
                # îl marcăm în Redis imediat, TTL = 24h
                r.setex(redis_key, TTL_24H, json.dumps(data))
        if len(cohort) >= max_users:
            break
    return dict(cohort)
