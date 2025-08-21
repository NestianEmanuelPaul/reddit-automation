from app.utils.logger import logger

def generate_message(user_data):
    # Exemplu simplu de generare
    name = user_data.get("name", "Redditor")
    message = f"Salut {name}, am văzut postările tale interesante!"
    logger.info(f"📝 Mesaj generat pentru {name}")
    return message
