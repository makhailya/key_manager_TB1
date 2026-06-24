# 🔐 Key Manager API — TB1

Асинхронный REST API сервис для безопасного хранения секретных ключей, API токенов и паролей.

## Стек технологий

| Компонент | Технология |
|---|---|
| Фреймворк | FastAPI (async) |
| База данных | MongoDB |
| ODM | Beanie |
| Аутентификация | JWT (python-jose) |
| Шифрование | Fernet / cryptography |
| Контейнеризация | Docker + Docker Compose |
| Тесты | pytest + httpx + mongomock |

## Архитектура

```
┌──────────────┐    JWT     ┌─────────────────────────────┐
│   Клиент     │ ─────────► │        FastAPI (async)       │
│  (Swagger/   │            │                             │
│   curl/...)  │ ◄───────── │  routers → services → ODM  │
└──────────────┘  JSON resp └──────────────┬──────────────┘
                                           │ Beanie (Motor)
                                           ▼
                                   ┌───────────────┐
                                   │   MongoDB      │
                                   │  (зашифр. данные) │
                                   └───────────────┘
```

## Запуск

### Через Docker Compose (рекомендуется)

```bash
# 1. Клонируй репозиторий
git clone https://github.com/your-username/tb1-key-manager.git
cd tb1-key-manager

# 2. Создай .env файл
cp .env.example .env

# 3. Сгенерируй Fernet ключ и добавь в .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Скопируй результат в FERNET_KEY в .env

# 4. Запусти
docker-compose up --build

# API доступен на: http://localhost:8000
# Swagger документация: http://localhost:8000/docs
```

### Локально через Poetry

```bash
# Установи зависимости
poetry install

# Активируй виртуальное окружение
poetry shell

# Запусти (нужна запущенная MongoDB на localhost:27017)
uvicorn app.main:app --reload
```

## API Endpoints

| Метод | URL | Описание | Auth |
|---|---|---|---|
| POST | `/auth/register` | Регистрация | ❌ |
| POST | `/auth/login` | Получить JWT | ❌ |
| GET | `/auth/me` | Мои данные | ✅ |
| GET | `/keys` | Список ключей | ✅ |
| POST | `/keys` | Создать ключ | ✅ |
| GET | `/keys/{id}` | Получить ключ | ✅ |
| PATCH | `/keys/{id}` | Обновить ключ | ✅ |
| DELETE | `/keys/{id}` | Удалить ключ | ✅ |

### Пример использования

```bash
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'

# Логин — получаем JWT
curl -X POST http://localhost:8000/auth/login \
  -F "username=user@example.com" \
  -F "password=mypassword"

# Создание ключа
curl -X POST http://localhost:8000/keys \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "GitHub Token", "value": "ghp_secret123", "tags": ["github"]}'
```

## Безопасность

- **Пароли** хэшируются алгоритмом `bcrypt` — необратимое преобразование
- **Значения ключей** шифруются алгоритмом `Fernet` (AES-128-CBC + HMAC)
- **JWT токены** подписаны секретным ключом, срок действия — 60 минут
- **Изоляция данных** — пользователь видит только свои ключи

## Тестирование

```bash
# Запуск тестов
poetry run pytest -v

# С отчётом о покрытии
poetry run pytest --cov=app --cov-report=term-missing
```

## Структура проекта

```
tb1_key_manager/
├── app/
│   ├── main.py              # Точка входа
│   ├── config.py            # Настройки (pydantic-settings)
│   ├── database.py          # Подключение MongoDB
│   ├── dependencies.py      # FastAPI DI (get_current_user)
│   ├── models/              # Beanie Documents (MongoDB)
│   ├── schemas/             # Pydantic схемы (API)
│   ├── routers/             # Эндпоинты
│   └── services/            # Бизнес-логика
├── tests/                   # pytest тесты
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Автор

Ilya Makhanek — дипломный проект TB1
