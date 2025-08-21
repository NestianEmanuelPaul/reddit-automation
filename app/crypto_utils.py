from cryptography.fernet import Fernet
import json
import os

KEY_FILE = "secret.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

def encrypt_data(data: dict, filename: str):
    key = load_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(data).encode())
    with open(filename, "wb") as file:
        file.write(encrypted)

def decrypt_data(filename: str) -> dict:
    key = load_key()
    fernet = Fernet(key)
    if not os.path.exists(filename):
        return {}
    with open(filename, "rb") as file:
        encrypted = file.read()
    try:
        return json.loads(fernet.decrypt(encrypted).decode())
    except:
        return {}
