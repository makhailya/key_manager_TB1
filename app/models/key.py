"""
models/key.py — модель «ключа» (секрета) в MongoDB.

Каждый ключ принадлежит конкретному пользователю (owner_id).
Значение ключа хранится в ЗАШИФРОВАННОМ виде (encrypted_value).
Даже если кто-то взломает БД — он увидит только зашифрованный blob.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class Key(Document):
    """
    Коллекция 'keys' в MongoDB.
    Каждый документ — один секрет пользователя.
    """

    owner_id: Annotated[str, Indexed()]
    name: str                   # человекочитаемое название: "GitHub Token", "AWS Key"
    description: str | None = None
    encrypted_value: str        # ЗАШИФРОВАННОЕ значение ключа (Fernet)
    tags: list[str] = []        # теги для фильтрации: [aws, production]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "keys"
