# CHANGELOG

## Исправления (2026-06-25)

### 0. `app/models/key.py`, `app/models/user.py` — тип `Indexed` через `Annotated`
**Проблема:** PyCharm/mypy ругаются "Invalid type annotation" на `Indexed(str)` и `Indexed(EmailStr, unique=True)`, поскольку `Indexed` — функция, а её возврат используется как аннотация типа.

**Исправление:** заменено на корректный синтаксис через `typing.Annotated`:
- `owner_id: Indexed(str)` → `owner_id: Annotated[str, Indexed()]`
- `email: Indexed(EmailStr, unique=True)` → `email: Annotated[EmailStr, Indexed(unique=True)]`

Beanie поддерживает `Annotated` начиная с версии 1.30.0: метаданные `IndexedAnnotation` распознаются при построении индексов.

### 1. `app/services/auth_service.py` — замена passlib на прямой bcrypt
**Проблема:** `passlib` несовместим с `bcrypt>=4.1` на Python 3.14. При инициализации `CryptContext` библиотека passlib вызывает внутренние методы bcrypt, которые были удалены в версии 4.1+ (модуль `__about__`). Это приводило к `AttributeError` и падению всех тестов, связанных с регистрацией/логином.

**Исправление:** заменён `passlib.context.CryptContext` на прямой вызов `bcrypt.hashpw()` / `bcrypt.checkpw()`.

### 2. `app/routers/keys.py` — неверный Beanie-запрос фильтрации по тегу
**Проблема:** в `list_keys()` при фильтрации по тегу использовался неверный синтаксис:
```python
Key.find(Key.owner_id == str(current_user.id), {"tags": tag})
```
Beanie не принимает сырой словарь `{"tags": tag}` как второй позиционный аргумент.

**Исправление:**
```python
Key.find(Key.owner_id == str(current_user.id), Key.tags == tag)
```

### 3. `app/routers/keys.py` — неиспользуемый импорт
Удалён импорт `PydanticObjectId` из `beanie`.

### 4. `app/models/key.py` — неиспользуемые импорты
Удалены импорты `Link` и `User` (не использовались в модели).

### 5. `app/models/key.py`, `app/models/user.py`, `app/routers/keys.py` — `datetime.utcnow()` deprecated
**Проблема:** `datetime.utcnow()` объявлен устаревшим в Python 3.12 и удалён в 3.14.

**Исправление:** заменено на `datetime.now(timezone.utc)` (через `lambda` для `Field(default_factory=...)`).

### 6. `pyproject.toml` — зависимости
- Удалена `passlib = {extras = ["bcrypt"], version = "^1.7.4"}`
- Добавлена `bcrypt = "^4.1.0"` 
- Добавлена конфигурация `packages = [{include = "app"}]` для корректной установки проекта

### Результат
- Все 17 тестов проходят (было: 1 failed, 11 errors, 5 passed).
- Код совместим с Python 3.13/3.14.
- Устранены deprecation warnings.
