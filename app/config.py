"""
config.py — централизованные настройки приложения.

Pydantic-settings автоматически читает переменные из .env файла.
Это лучшая практика: никаких магических строк по всему коду,
все настройки в одном месте.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- MongoDB ---
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db_name: str = "key_manager"

    # --- JWT ---
    secret_key: str = "fallback-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- Fernet (симметричное шифрование) ---
    fernet_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Создаём единственный экземпляр настроек для всего приложения
settings = Settings()
