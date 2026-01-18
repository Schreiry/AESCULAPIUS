# security_utils.py

from cryptography.fernet import Fernet, InvalidToken
from werkzeug.security import generate_password_hash, check_password_hash
from config import ENCRYPTION_KEY

# Убедимся, что ключ загружен
if not ENCRYPTION_KEY or ENCRYPTION_KEY == b"your-fernet-key-will-be-placed-here":
    raise ValueError("ENCRYPTION_KEY не установлен в config.py. Сначала сгенерируйте его с помощью setup_security.py.")

cipher_suite = Fernet(ENCRYPTION_KEY)

# --- Функции для шифрования данных ---

def encrypt_data(data: str) -> str:
    """Шифрует строку и возвращает ее в виде строки base64."""
    if not data:
        return data
    encrypted_bytes = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """Расшифровывает строку. В случае ошибки возвращает 'CORRUPTED'."""
    if not encrypted_data:
        return encrypted_data
    try:
        decrypted_bytes = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except (InvalidToken, TypeError):
        # InvalidToken - ошибка расшифровки, TypeError может быть, если данные не байты
        return "CORRUPTED"

# --- Функции для хеширования паролей ---

def hash_password(password: str) -> str:
    """Генерирует хеш для пароля."""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

def verify_password(hashed_password: str, password: str) -> bool:
    """Проверяет, соответствует ли пароль хешу."""
    return check_password_hash(hashed_password, password)
