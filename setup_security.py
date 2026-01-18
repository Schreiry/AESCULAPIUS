# setup_security.py
# Этот скрипт нужно запустить один раз для генерации ключей и хешей.

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

def generate_keys_and_hashes():
    """
    Генерирует ключ шифрования Fernet и хеши паролей для стартовых пользователей.
    """
    print("--- Генерация Ключа Шифрования (Fernet) ---")
    fernet_key = Fernet.generate_key()
    print("Скопируйте этот ключ в файл config.py, в переменную ENCRYPTION_KEY:")
    print(f"ENCRYPTION_KEY = {fernet_key}\n")

    print("--- Генерация Хешей Паролей ---")
    users = [
        ('ChiefArchi', '24\Quis-Сustodiet-ips@s_cust@des|19'),
        ('admin_wolf', '\\\HeAl_or-Does_iT-HuRt?@@\\\ '),
        ('admin_house', 'vicodin'),
        ('admin_strange', 'dormammu'),
        ('nurse_joy', 'pokemon_center_123')
    ]

    print("Скопируйте сгенерированные хеши в ваш SQL-скрипт (Nbase.sql) для обновления паролей пользователей.\n")
    for user, pwd in users:
        # Используем более безопасный метод хеширования pbkdf2
        hashed_password = generate_password_hash(pwd, method='pbkdf2:sha256', salt_length=8)
        print(f"-- User: {user}")
        print(f"UPDATE Users SET PasswordHash = '{hashed_password}' WHERE Login = '{user}';")
    
    print("\n---")
    print("Не забудьте также обновить структуру таблиц в Nbase.sql, как указано в следующем шаге.")


if __name__ == "__main__":
    generate_keys_and_hashes()
