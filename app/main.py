"""
main.py — точка входа FastAPI приложения.

Здесь происходит:
1. Создание FastAPI экземпляра
2. Настройка lifespan (что делать при старте/остановке)
3. Подключение CORS (разрешаем запросы с фронтенда)
4. Подключение роутеров
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, keys


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    lifespan — управление жизненным циклом приложения.
    
    Код ДО yield — выполняется при старте (как __init__)
    Код ПОСЛЕ yield — выполняется при остановке (как __del__)
    
    Аналогия: это как включение и выключение света в комнате.
    Входишь — свет включается, выходишь — выключается.
    """
    # Старт: подключаемся к MongoDB
    await init_db()
    print("✅ База данных подключена")
    yield
    # Остановка: можно закрыть соединения (Motor закрывает сам)
    print("🔴 Приложение остановлено")


app = FastAPI(
    title="🔐 Key Manager API",
    description="""
## Менеджер секретных ключей

Безопасное хранилище для API ключей, паролей и токенов.

### Возможности
- 🔑 **Хранение ключей** с шифрованием Fernet (AES-128)
- 👤 **Аутентификация** через JWT токены
- 🏷️ **Теги** для организации ключей
- 🔒 **Изоляция** — каждый пользователь видит только свои ключи

### Как начать
1. `POST /auth/register` — зарегистрируйтесь
2. `POST /auth/login` — получите JWT токен
3. Нажмите **Authorize** выше и вставьте токен
4. Используйте `/keys` для управления секретами
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — разрешаем запросы с любых доменов (для разработки)
# В продакшене укажи конкретные домены: ["https://yourfrontend.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(keys.router)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Проверка работоспособности сервиса (health check)."""
    return {"status": "ok", "service": "Key Manager API", "version": "1.0.0"}
