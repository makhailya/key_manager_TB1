"""
generate_keys.py — утилита для генерации секретных ключей.

Запусти ОДИН РАЗ при первом развёртывании:
    python generate_keys.py

Скопируй результат в .env файл.
"""

import secrets
from cryptography.fernet import Fernet


def main():
    print("=" * 55)
    print("  Генератор секретных ключей для .env")
    print("=" * 55)
    print()

    fernet_key = Fernet.generate_key().decode()
    jwt_secret = secrets.token_hex(32)

    print("Добавь эти строки в свой .env файл:\n")
    print(f"SECRET_KEY={jwt_secret}")
    print(f"FERNET_KEY={fernet_key}")
    print()
    print("⚠️  ВАЖНО: Сохрани FERNET_KEY в надёжном месте!")
    print("   Если потеряешь — не сможешь расшифровать сохранённые ключи.")
    print("=" * 55)


if __name__ == "__main__":
    main()
