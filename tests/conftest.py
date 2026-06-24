"""
tests/conftest.py — фикстуры для тестов.

conftest.py — специальный файл pytest. Фикстуры, объявленные здесь,
доступны во ВСЕХ тестовых файлах автоматически.

Мы используем mongomock-motor — это «фиктивная» MongoDB в памяти.
Тесты не нужна реальная БД!

Аналогия: как тренажёр в спортзале — выглядит как настоящий,
работает похоже, но не нужно идти на настоящую гору.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.models.user import User
from app.models.key import Key


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["test_db"],
        document_models=[User, Key],
    )
    yield


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Регистрирует тестового пользователя и возвращает его данные."""
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, registered_user: dict) -> dict:
    """
    Логинится и возвращает заголовки с JWT токеном.
    Используй как: async def test_something(client, auth_headers):
    """
    response = await client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
