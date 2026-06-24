"""
models/user.py — модель пользователя в MongoDB.

Beanie Document — это Python класс, который автоматически
превращается в коллекцию в MongoDB.

Аналогия: если MongoDB — это Excel, то Document — это схема одного листа.
"""

from datetime import datetime
from beanie import Document, Indexed
from pydantic import EmailStr, Field


class User(Document):
    """
    Коллекция 'users' в MongoDB.
    Хранит зарегистрированных пользователей.
    """

    email: Indexed(EmailStr, unique=True)  # уникальный индекс — нельзя два одинаковых email
    hashed_password: str                   # храним ХЭШ, никогда не сам пароль!
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"  # название коллекции в MongoDB
