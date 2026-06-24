"""
routers/keys.py — CRUD для секретов/ключей пользователя.

GET    /keys          — список всех ключей (без значений)
POST   /keys          — создать новый ключ
GET    /keys/{key_id} — получить ключ с расшифрованным значением
PATCH  /keys/{key_id} — частично обновить ключ
DELETE /keys/{key_id} — удалить ключ

Все эндпоинты защищены JWT — нужен Depends(get_current_user).
Каждый пользователь видит ТОЛЬКО свои ключи.
"""

from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.models.key import Key
from app.models.user import User
from app.schemas.key import KeyCreate, KeyUpdate, KeyResponse, KeyListResponse
from app.services.crypto_service import crypto_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/keys", tags=["Ключи"])


@router.get(
    "",
    response_model=list[KeyListResponse],
    summary="Список ключей пользователя",
)
async def list_keys(
    tag: str | None = Query(default=None, description="Фильтр по тегу"),
    current_user: User = Depends(get_current_user),
) -> list[KeyListResponse]:
    """
    Возвращает список ключей текущего пользователя.
    Значения (value) НЕ включены — только метаданные.
    Можно фильтровать по тегу: GET /keys?tag=aws
    """
    query = Key.find(Key.owner_id == str(current_user.id))

    if tag:
        # MongoDB: ищем документы, где массив tags содержит нужный тег
        query = Key.find(Key.owner_id == str(current_user.id), {"tags": tag})

    keys = await query.to_list()

    return [
        KeyListResponse(
            id=str(k.id),
            name=k.name,
            description=k.description,
            tags=k.tags,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.post(
    "",
    response_model=KeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый ключ",
)
async def create_key(
    key_data: KeyCreate,
    current_user: User = Depends(get_current_user),
) -> KeyResponse:
    """
    Создаёт новый ключ.
    Значение (value) шифруется перед сохранением в MongoDB.
    """
    # Шифруем значение перед сохранением
    encrypted = crypto_service.encrypt(key_data.value)

    new_key = Key(
        owner_id=str(current_user.id),
        name=key_data.name,
        description=key_data.description,
        encrypted_value=encrypted,
        tags=key_data.tags,
    )
    await new_key.insert()

    return KeyResponse(
        id=str(new_key.id),
        name=new_key.name,
        value=key_data.value,  # возвращаем оригинал (уже есть в памяти)
        description=new_key.description,
        tags=new_key.tags,
        created_at=new_key.created_at,
        updated_at=new_key.updated_at,
    )


@router.get(
    "/{key_id}",
    response_model=KeyResponse,
    summary="Получить ключ с расшифрованным значением",
)
async def get_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
) -> KeyResponse:
    """
    Возвращает конкретный ключ с расшифрованным значением.
    Проверяет, что ключ принадлежит текущему пользователю.
    """
    key = await Key.get(key_id)

    if not key:
        raise HTTPException(status_code=404, detail="Ключ не найден")

    # Проверка владельца — важно! Нельзя читать чужие ключи
    if key.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    # Расшифровываем значение
    decrypted_value = crypto_service.decrypt(key.encrypted_value)

    return KeyResponse(
        id=str(key.id),
        name=key.name,
        value=decrypted_value,
        description=key.description,
        tags=key.tags,
        created_at=key.created_at,
        updated_at=key.updated_at,
    )


@router.patch(
    "/{key_id}",
    response_model=KeyResponse,
    summary="Обновить ключ",
)
async def update_key(
    key_id: str,
    key_data: KeyUpdate,
    current_user: User = Depends(get_current_user),
) -> KeyResponse:
    """
    Частично обновляет ключ (PATCH = только изменённые поля).
    Если передано новое value — перешифровывает его.
    """
    key = await Key.get(key_id)

    if not key:
        raise HTTPException(status_code=404, detail="Ключ не найден")

    if key.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    # Обновляем только переданные поля
    update_data: dict = {}

    if key_data.name is not None:
        update_data["name"] = key_data.name
    if key_data.description is not None:
        update_data["description"] = key_data.description
    if key_data.tags is not None:
        update_data["tags"] = key_data.tags
    if key_data.value is not None:
        update_data["encrypted_value"] = crypto_service.encrypt(key_data.value)

    update_data["updated_at"] = datetime.utcnow()

    await key.set(update_data)

    # Перезагружаем из БД для актуальных данных
    await key.sync()

    decrypted_value = crypto_service.decrypt(key.encrypted_value)

    return KeyResponse(
        id=str(key.id),
        name=key.name,
        value=decrypted_value,
        description=key.description,
        tags=key.tags,
        created_at=key.created_at,
        updated_at=key.updated_at,
    )


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ключ",
)
async def delete_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Удаляет ключ. 204 No Content = успех без тела ответа."""
    key = await Key.get(key_id)

    if not key:
        raise HTTPException(status_code=404, detail="Ключ не найден")

    if key.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    await key.delete()
