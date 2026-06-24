"""
routers/auth.py — эндпоинты аутентификации.

POST /auth/register — регистрация нового пользователя
POST /auth/login    — вход и получение JWT токена
GET  /auth/me       — информация о себе (защищённый)
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register(user_data: UserCreate) -> UserResponse:
    """
    Регистрирует нового пользователя.
    
    Шаги:
    1. Проверяем, не занят ли email
    2. Хэшируем пароль
    3. Сохраняем в MongoDB
    4. Возвращаем данные пользователя (без пароля)
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # Хэшируем пароль и создаём пользователя
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    await new_user.insert()

    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Вход и получение JWT токена",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Аутентифицирует пользователя и возвращает JWT.
    
    OAuth2PasswordRequestForm принимает form-data с полями:
    - username (мы используем как email)
    - password
    
    Почему form-data, а не JSON?
    Это стандарт OAuth2 — FastAPI и Swagger UI ожидают именно его.
    """
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=str(user.id))
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Информация о текущем пользователе",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Возвращает данные текущего аутентифицированного пользователя."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )
