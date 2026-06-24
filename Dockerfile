# Dockerfile — инструкция по сборке Docker образа.
#
# Аналогия: это как рецепт приготовления блюда.
# Docker читает рецепт и "готовит" контейнер с нашим приложением.
#
# Мы используем multi-stage build:
# Stage 1 (builder) — устанавливаем зависимости через Poetry
# Stage 2 (runtime) — берём только нужные файлы, без лишнего мусора

# ── Stage 1: builder ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /app

# Копируем файлы зависимостей (сначала — чтобы Docker кэшировал слой)
COPY pyproject.toml poetry.lock* ./

# Экспортируем зависимости в requirements.txt
# --without dev — без тестовых библиотек в продакшене
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# ── Stage 2: runtime ──────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Устанавливаем зависимости из requirements.txt
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app/ ./app/

# Порт, который слушает наше приложение
EXPOSE 8000

# Команда запуска:
# uvicorn — ASGI сервер для FastAPI
# app.main:app — путь к объекту FastAPI
# --host 0.0.0.0 — слушаем на всех интерфейсах (не только localhost)
# --port 8000 — порт
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
