from app.ai_client import generate_message
import random

def simulate_user_analysis(username: str, comments: str):
    # Pasul 1: generează text prietenos
    ai_text = generate_message(comments)

    # Pasul 2: scor aleator (simulare)
    score = round(random.uniform(0, 10), 2)

    # Pasul 3: afișare în consolă
    print("=" * 50)
    print(f"User analizat: {username}")
    print(f"Comentarii analizate:\n{comments.strip()}")
    print("-" * 50)
    print(f"Mesaj AI: {ai_text}")
    print(f"Scor: {score}/10")
    print("=" * 50)

if __name__ == "__main__":
    # Comentarii mock
    print("Pornim simulate_local...")

    sample_comments = """
    1. Îmi place foarte mult conținutul educativ despre programare.
    2. Cred că tutorialele pas-cu-pas sunt cele mai utile.
    3. Îmi displac postările care nu au exemple practice.
    """
    simulate_user_analysis("User_Test", sample_comments)
