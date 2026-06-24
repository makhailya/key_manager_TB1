"""
database.py — инициализация подключения к MongoDB.

Beanie — это async ODM (Object Document Mapper) для MongoDB.
Он работает поверх Motor (async MongoDB driver).

Аналогия: Beanie для MongoDB — это как Django ORM для PostgreSQL,
только асинхронный и для документной базы данных.
"""

import motor.motor_asyncio
from beanie import init_beanie

from app.config import settings
from app.models.user import User
from app.models.key import Key


async def init_db() -> None:
    """
    Инициализирует соединение с MongoDB и регистрирует модели Beanie.
    Вызывается один раз при старте приложения (lifespan).
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
    database = client[settings.mongo_db_name]

    # Регистрируем все Beanie-документы (модели).
    # Beanie создаст коллекции и индексы автоматически.
    await init_beanie(
        database=database,
        document_models=[User, Key],
    )
