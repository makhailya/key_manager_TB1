"""
models/user.py — модель пользователя в MongoDB.

Beanie Document — это Python класс, который автоматически
превращается в коллекцию в MongoDB.

Аналогия: если MongoDB — это Excel, то Document — это схема одного листа.
"""

from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    """
    Коллекция 'users' в MongoDB.
    Хранит зарегистрированных пользователей.
    """

    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str                   # храним ХЭШ, никогда не сам пароль!
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"  # название коллекции в MongoDB
