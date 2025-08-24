import requests

API_URL = "http://localhost:8000/suggest"  # sau URL-ul public al backend-ului tău

def get_users_and_history():
    # Simulare - în practică citești din baza de date / pipeline
    return [
        {
            "user_id": "Emanuel2010Romania",
            "features": {"karma": 120, "joined_days": 450},
            "history": [
                "Îmi place să călătoresc în natură",
                "Caut sfaturi pentru fotografie"
            ]
        },
        {
            "user_id": "alt_user",
            "features": {"karma": 50, "joined_days": 30},
            "history": [
                "Fan jocuri video indie",
                "Îmi place pixel art"
            ]
        }
    ]

payload = {
    "user_id": "test_user",
    "features": {"karma": 100, "joined_days": 50},
    "history": [
        "Salut, mă bucur să ne conectăm.",
        "Cum merge proiectul la care lucrezi?"
    ]
}

r = requests.post(API_URL, json=payload)
if r.status_code == 200:
    data = r.json()
    print(f"Sugestii pentru {data['user_id']}:")
    for sug in data["suggestions"]:
        print(f"- {sug['message']} (score={sug['score']})")
else:
    print("Eroare:", r.status_code, r.text)

""" def main():
    for user in get_users_and_history():
        try:
            resp = requests.post(API_URL, json=user, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            print(f"Răspuns pentru {data['user_id']}:")
            for s in data["suggestions"]:
                print(f" - {s['message']} (scor={s['score']})")
        except requests.RequestException as e:
            print(f"Eroare la {user['user_id']}: {e}")

if __name__ == "__main__":
    main() """
