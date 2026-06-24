"""
models/key.py — модель «ключа» (секрета) в MongoDB.

Каждый ключ принадлежит конкретному пользователю (owner_id).
Значение ключа хранится в ЗАШИФРОВАННОМ виде (encrypted_value).
Даже если кто-то взломает БД — он увидит только зашифрованный blob.
"""

from datetime import datetime
from beanie import Document, Link, Indexed
from pydantic import Field

from app.models.user import User


class Key(Document):
    """
    Коллекция 'keys' в MongoDB.
    Каждый документ — один секрет пользователя.
    """

    owner_id: Indexed(str)      # ID пользователя-владельца (индекс для быстрого поиска)
    name: str                   # человекочитаемое название: "GitHub Token", "AWS Key"
    description: str | None = None
    encrypted_value: str        # ЗАШИФРОВАННОЕ значение ключа (Fernet)
    tags: list[str] = []        # теги для фильтрации: ["aws", "production"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "keys"
