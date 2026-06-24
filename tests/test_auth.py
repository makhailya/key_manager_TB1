"""
tests/test_auth.py — тесты для эндпоинтов аутентификации.

Принцип тестирования: AAA (Arrange-Act-Assert)
- Arrange (Подготовка): подготавливаем данные
- Act (Действие): вызываем эндпоинт
- Assert (Проверка): проверяем результат
"""

from httpx import AsyncClient


class TestRegister:
    """Тесты для POST /auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """Успешная регистрация нового пользователя."""
        # Act
        response = await client.post("/auth/register", json={
            "email": "new@example.com",
            "password": "password123",
        })

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "password" not in data       # пароль никогда не возвращаем!
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient, registered_user: dict):
        """Нельзя зарегистрировать два аккаунта с одним email."""
        response = await client.post("/auth/register", json={
            "email": "test@example.com",  # уже занят (из фикстуры)
            "password": "another_pass",
        })

        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]

    async def test_register_invalid_email(self, client: AsyncClient):
        """Невалидный email отклоняется Pydantic."""
        response = await client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
        })

        assert response.status_code == 422  # Unprocessable Entity


class TestLogin:
    """Тесты для POST /auth/login"""

    async def test_login_success(self, client: AsyncClient, registered_user: dict):
        """Успешный вход возвращает JWT токен."""
        response = await client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "testpass123",
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, registered_user: dict):
        """Неверный пароль → 401."""
        response = await client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "wrong_password",
        })

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Несуществующий пользователь → 401."""
        response = await client.post("/auth/login", data={
            "username": "ghost@example.com",
            "password": "password",
        })

        assert response.status_code == 401


class TestGetMe:
    """Тесты для GET /auth/me"""

    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict):
        """Авторизованный пользователь получает свои данные."""
        response = await client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    async def test_get_me_no_token(self, client: AsyncClient):
        """Без токена → 401."""
        response = await client.get("/auth/me")

        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Невалидный токен → 401."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401
