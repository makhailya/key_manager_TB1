"""
schemas/user.py — Pydantic схемы для пользователей.

Важно понять разницу:
- Model (Beanie Document) = как данные хранятся в MongoDB
- Schema (Pydantic) = как данные выглядят в API запросах/ответах

Это разделение — лучшая практика. Мы никогда не возвращаем
hashed_password через API — он есть в модели, но не в схеме ответа.
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Тело запроса POST /auth/register"""
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    """Тело ответа — что видит клиент. БЕЗ пароля!"""
    id: str
    email: EmailStr
    full_name: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT токен в ответе на /auth/login"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные внутри JWT токена (payload)"""
    user_id: str | None = None
