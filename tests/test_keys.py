"""
tests/test_keys.py — тесты для CRUD операций с ключами.
"""

import pytest
from httpx import AsyncClient


class TestCreateKey:
    """Тесты для POST /keys"""

    async def test_create_key_success(self, client: AsyncClient, auth_headers: dict):
        """Успешное создание ключа с шифрованием."""
        response = await client.post("/keys", json={
            "name": "GitHub Token",
            "value": "ghp_secretToken123",
            "description": "Мой GitHub Personal Access Token",
            "tags": ["github", "dev"],
        }, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "GitHub Token"
        assert data["value"] == "ghp_secretToken123"  # возвращается расшифрованным
        assert "id" in data

    async def test_create_key_unauthorized(self, client: AsyncClient):
        """Без токена → 401."""
        response = await client.post("/keys", json={
            "name": "Test Key",
            "value": "secret",
        })
        assert response.status_code == 401


class TestGetKeys:
    """Тесты для GET /keys"""

    async def test_list_keys_empty(self, client: AsyncClient, auth_headers: dict):
        """Новый пользователь видит пустой список."""
        response = await client.get("/keys", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_list_keys_with_data(self, client: AsyncClient, auth_headers: dict):
        """После создания ключей список не пустой."""
        # Создаём два ключа
        await client.post("/keys", json={"name": "Key 1", "value": "val1"}, headers=auth_headers)
        await client.post("/keys", json={"name": "Key 2", "value": "val2"}, headers=auth_headers)

        response = await client.get("/keys", headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_list_keys_isolation(self, client: AsyncClient, auth_headers: dict):
        """
        Пользователь A не видит ключи пользователя B.
        Это критически важный тест для безопасности!
        """
        # Создаём ключ для пользователя A (auth_headers)
        await client.post("/keys", json={"name": "Key A", "value": "val_a"}, headers=auth_headers)

        # Регистрируем пользователя B
        await client.post("/auth/register", json={
            "email": "userb@example.com",
            "password": "passB123",
        })
        login_b = await client.post("/auth/login", data={
            "username": "userb@example.com",
            "password": "passB123",
        })
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        # Пользователь B видит 0 ключей
        response_b = await client.get("/keys", headers=headers_b)
        assert len(response_b.json()) == 0


class TestGetKey:
    """Тесты для GET /keys/{id}"""

    async def test_get_key_success(self, client: AsyncClient, auth_headers: dict):
        """Получение ключа с расшифрованным значением."""
        # Создаём ключ
        create_resp = await client.post("/keys", json={
            "name": "AWS Key",
            "value": "AKIAIOSFODNN7EXAMPLE",
        }, headers=auth_headers)
        key_id = create_resp.json()["id"]

        # Получаем ключ
        response = await client.get(f"/keys/{key_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["value"] == "AKIAIOSFODNN7EXAMPLE"  # расшифровано!

    async def test_get_foreign_key_forbidden(self, client: AsyncClient, auth_headers: dict):
        """Нельзя читать чужой ключ."""
        # Создаём ключ пользователем A
        create_resp = await client.post("/keys", json={"name": "K", "value": "v"}, headers=auth_headers)
        key_id = create_resp.json()["id"]

        # Пользователь B пытается прочитать
        await client.post("/auth/register", json={"email": "b@b.com", "password": "bbbbb123"})
        login_b = await client.post("/auth/login", data={"username": "b@b.com", "password": "bbbbb123"})
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        response = await client.get(f"/keys/{key_id}", headers=headers_b)
        assert response.status_code == 403


class TestDeleteKey:
    """Тесты для DELETE /keys/{id}"""

    async def test_delete_key_success(self, client: AsyncClient, auth_headers: dict):
        """Успешное удаление ключа."""
        create_resp = await client.post("/keys", json={"name": "K", "value": "v"}, headers=auth_headers)
        key_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/keys/{key_id}", headers=auth_headers)
        assert delete_resp.status_code == 204

        # После удаления — 404
        get_resp = await client.get(f"/keys/{key_id}", headers=auth_headers)
        assert get_resp.status_code == 404
