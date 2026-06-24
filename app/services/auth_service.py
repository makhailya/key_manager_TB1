"""
services/auth_service.py — сервис аутентификации.

Два важных понятия:

1. Хэширование паролей (bcrypt):
   - Одностороннее преобразование: "password123" → "$2b$12$..."
   - Нельзя «расшифровать» хэш обратно в пароль
   - При проверке: хэшируем снова и сравниваем хэши
   - Аналогия: кофемолка. Из зёрен можно сделать кофе, но не наоборот.

2. JWT (JSON Web Token):
   - Подписанный токен, который содержит данные о пользователе
   - Состоит из 3 частей: header.payload.signature
   - Сервер не хранит токены — он их только проверяет подпись
   - Аналогия: паспорт. Содержит данные и подпись государства.
     Любой банк может проверить подлинность без звонка в паспортный стол.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# CryptContext — контекст для работы с паролями
# bcrypt — самый надёжный алгоритм хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Превращает открытый пароль в bcrypt хэш."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли открытый пароль с хэшем.
    НИКОГДА не сравниваем пароли напрямую!
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """
    Создаёт JWT токен с ID пользователя внутри.
    
    Что кладём в payload:
    - sub (subject) = ID пользователя
    - exp (expiration) = когда токен истекает
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": user_id,  # subject — кто этот токен
        "exp": expire,   # expiration — когда истекает
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str | None:
    """
    Декодирует JWT токен и возвращает user_id.
    Если токен невалидный или просроченный — возвращает None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str | None = payload.get("sub")
        return user_id
    except JWTError:
        return None
