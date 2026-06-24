"""
dependencies.py — FastAPI Dependency Injection (внедрение зависимостей).

Зависимость get_current_user делает следующее:
1. Берёт токен из заголовка Authorization: Bearer <token>
2. Декодирует JWT → получает user_id
3. Загружает пользователя из MongoDB
4. Возвращает объект User — доступен в любом роутере

Аналогия: это как турникет в метро. Каждый защищённый эндпоинт
«проходит через турникет», который проверяет билет (JWT).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.services.auth_service import decode_access_token

# OAuth2PasswordBearer автоматически читает токен из заголовка
# tokenUrl — куда пользователь должен идти за токеном
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Зависимость: извлекает и возвращает текущего пользователя по JWT.
    
    Используется в роутерах так:
        async def some_endpoint(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = await User.get(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь деактивирован",
        )

    return user
