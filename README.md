# Petstore API Tests (Python + Pytest + requests)

Проект с автотестами для публичного стенда `https://petstore.swagger.io`.
Цель — показать уверенную работу с REST API, структурой тестов и инструментами.

## Стек

- Python 3.10+
- pytest
- requests
- Faker — живые рандомные данные (имена, слова, URL)
- black / isort / flake8 — автоформатирование и линтинг

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Base URL

По умолчанию используется `https://petstore.swagger.io/v2`.

Можно переопределить через переменную окружения:

```bash
export PETSTORE_BASE_URL="https://petstore.swagger.io/v2"
pytest
```

## Что проверяют тесты

Основной фокус — раздел `/pet`:

- `POST /pet` — создание питомца
- `GET /pet/{id}` — чтение
- `PUT /pet` — обновление
- `DELETE /pet/{id}` — удаление
- `GET /pet/findByStatus` — поиск по статусу

Покрыты:

- позитивные сценарии (CRUD, поиск, обновление разными способами)
- негативные сценарии (невалидные ID, отсутствие обязательных полей и т.п.)
- более гибкие проверки, учитывающие нестабильность демо-стенда

## Структура проекта

```text
petstore-tests-python
├── README.md
├── requirements.txt
├── pytest.ini
├── pyproject.toml
├── src
│   ├── __init__.py
│   └── api_client.py
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_pet_crud.py
    ├── test_pet_search.py
    └── test_pet_negative.py
```

## Инструменты качества кода

```bash
black .
isort .
flake8 .
```

- **black** — автоформатирование кода
- **isort** — сортировка импортов
- **flake8** — базовый стиль и простые ошибки

## Pytest-марки

В `pytest.ini` определены маркеры:

- `@pytest.mark.smoke` — быстрые смоук-тесты
- `@pytest.mark.negative` — негативные сценарии
- `@pytest.mark.api` — все API-тесты

Примеры:

```bash
pytest -m smoke
pytest -m negative
pytest -m "api and not negative"
```
