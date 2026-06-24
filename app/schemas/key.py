"""
schemas/key.py — Pydantic схемы для ключей/секретов.

Здесь важный момент: клиент отправляет ОТКРЫТОЕ значение ключа (value),
а мы его шифруем и сохраняем как encrypted_value.
При чтении — расшифровываем и возвращаем value.
Клиент никогда не видит encrypted_value.
"""

from datetime import datetime
from pydantic import BaseModel


class KeyCreate(BaseModel):
    """Тело запроса POST /keys — создание нового ключа"""
    name: str
    value: str              # открытое значение, мы его зашифруем
    description: str | None = None
    tags: list[str] = []


class KeyUpdate(BaseModel):
    """Тело запроса PATCH /keys/{id} — частичное обновление"""
    name: str | None = None
    value: str | None = None  # если передан — перешифруем
    description: str | None = None
    tags: list[str] | None = None


class KeyResponse(BaseModel):
    """Тело ответа — ключ с расшифрованным значением"""
    id: str
    name: str
    value: str              # расшифрованное значение
    description: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KeyListResponse(BaseModel):
    """Краткое представление в списке (без значения — для безопасности)"""
    id: str
    name: str
    description: str | None
    tags: list[str]
    created_at: datetime
