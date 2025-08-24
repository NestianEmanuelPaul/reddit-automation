from app.services.auth_service import reddit_login
from app.services.parsing_service import get_recent_users
from app.services.storage_service import upsert_username_list
# from settings import REDDIT_USER, REDDIT_PASS, HF_API_KEY


USERNAME = "daniellikescoffee123"
PASSWORD = "RNeixv617fjv6nJ*Yfc+q3k!3R"  # parola de test

def separator(title):
    print("\n" + "=" * 60)
    print(f"[ {title} ]")
    print("=" * 60)

if __name__ == "__main__":
    separator("PAS 1 - LOGIN PE REDDIT")
    logged_in, session = reddit_login(USERNAME, PASSWORD)
    if not logged_in:
        print("[EROARE] Autentificare eșuată. Verifică user/parola sau conexiunea.")
        exit(1)
    else:
        print("[OK] Autentificare reușită.")

    separator("PAS 2 - SCRAPING UTILIZATORI")
    usernames = get_recent_users(session, subreddit="AskReddit", limit=10)
    print(f"[DEBUG] Lista brută de utilizatori: {usernames}")

    if not usernames:
        print("[WARN] Nu s-a găsit niciun utilizator.")
    else:
        print(f"[OK] Am extras {len(usernames)} utilizatori unici.")

    separator("PAS 3 - SALVARE ÎN BAZA DE DATE")
    if usernames:
        upsert_username_list(usernames)
        print("[OK] Salvare finalizată.")
    else:
        print("[INFO] Nu avem ce salva în acest run.")

    separator("TEST FINALIZAT")
    print("[INFO] Scriptul de test s-a terminat fără erori fatale.")
