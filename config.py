# config.py

# Ключ для сессий Flask и других нужд безопасности. 
# Используйте результат вывода `secrets.token_hex(16)` для генерации надежного ключа.
SECRET_KEY = "your-super-secret-flask-key"

# Ключ для шифрования данных пациентов (Fernet).
# Этот ключ будет сгенерирован и вставлен сюда на следующем шаге.
ENCRYPTION_KEY = b'v8TwfM4dFHpJVsX_qlPXl6w8olk5CCUaSMymfC020Gk='