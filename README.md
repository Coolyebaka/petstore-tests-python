# Автотесты для Petstore API (Yandex QA test task)

Профессиональная архитектура автотестов для API [petstore.swagger.io](https://petstore.swagger.io) с использованием Python, requests и pytest.

## Структура проекта

```
test-api/
├── api/                    # API клиенты
│   ├── __init__.py
│   └── client.py          # Универсальный HTTP клиент для всех эндпоинтов
├── tests/                  # Тестовые сценарии
│   ├── __init__.py
│   ├── conftest.py        # Общие фикстуры pytest
│   ├── test_pet.py        # Тесты для Pet API
│   ├── test_store.py      # Тесты для Store API
│   └── test_user.py       # Тесты для User API
├── utils/                  # Вспомогательные утилиты
│   ├── __init__.py
│   ├── validators.py      # Валидаторы ответов
│   ├── data_generators.py # Генераторы тестовых данных
│   └── logger.py          # Настройка логирования
├── config/                 # Конфигурация
│   ├── __init__.py
│   └── settings.py        # Настройки (URL, таймауты и т.д.)
├── pytest.ini             # Конфигурация pytest
├── requirements.txt       # Зависимости проекта
└── README.md             # Документация
```

## Установка

1. Создайте виртуальное окружение (если еще не создано):
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Запуск всех тестов
```bash
pytest
```

### Запуск тестов с подробным выводом
```bash
pytest -v
```

### Запуск тестов по маркерам

**Тесты для конкретного API:**
```bash
pytest -m pet      # Тесты Pet API
pytest -m store    # Тесты Store API
pytest -m user     # Тесты User API
```

**Позитивные тесты:**
```bash
pytest -m positive
```

**Негативные тесты:**
```bash
pytest -m negative
```

### Запуск конкретного тестового файла
```bash
pytest tests/test_pet.py
```

### Запуск конкретного теста
```bash
pytest tests/test_pet.py::TestPetAPI::test_create_pet
```

### Запуск с HTML отчетом
```bash
pytest --html=report.html --self-contained-html
```

## Конфигурация

Настройки можно изменить в файле `config/settings.py` или через переменные окружения:

- `PETSTORE_BASE_URL` - базовый URL API (по умолчанию: https://petstore.swagger.io/v2)
- `REQUEST_TIMEOUT` - таймаут запроса в секундах (по умолчанию: 30)
- `CONNECT_TIMEOUT` - таймаут подключения в секундах (по умолчанию: 10)
- `LOG_LEVEL` - уровень логирования (по умолчанию: INFO)
- `LOG_REQUESTS` - логировать запросы (по умолчанию: true)
- `LOG_RESPONSES` - логировать ответы (по умолчанию: true)
- `MAX_RETRIES` - максимальное количество повторов (по умолчанию: 3)
- `RETRY_DELAY` - задержка между повторами в секундах (по умолчанию: 1.0)

## Архитектура

### API Client (`api/client.py`)
Универсальный HTTP клиент с базовыми методами для работы с API:
- **Базовые HTTP методы**: `get()`, `post()`, `put()`, `patch()`, `delete()`
- **Поддержка базового пути**: можно создать клиент с предустановленным путем (например, `/pet`, `/user`, `/store`)
- Автоматическое логирование запросов/ответов
- Retry логика для неустойчивых соединений
- Обработка ошибок
- Управление сессией

**Преимущества подхода:**
- Масштабируемость: не нужно добавлять методы для каждого эндпоинта
- Изоляция тестов: каждый тестовый файл использует свой клиент с предустановленным путем
- Читаемость: в тестах явно видно, какой путь используется

### Фикстуры (`tests/conftest.py`)
- `api_client` - базовый API клиент без предустановленного пути
- `pet_client` - клиент с предустановленным путем `/pet`
- `store_client` - клиент с предустановленным путем `/store`
- `user_client` - клиент с предустановленным путем `/user`
- `pet_data`, `user_data`, `order_data` - генерация тестовых данных
- `created_pet`, `created_user`, `created_order` - создание и автоматическая очистка тестовых данных

### Валидаторы (`utils/validators.py`)
Функции для валидации ответов API:
- Проверка статус кодов
- Проверка структуры данных
- Валидация специфичных типов данных (Pet, User, Order)

### Генераторы данных (`utils/data_generators.py`)
Функции для генерации тестовых данных:
- `generate_pet_data()` - генерация данных питомца
- `generate_user_data()` - генерация данных пользователя
- `generate_order_data()` - генерация данных заказа

## Best Practices

1. **Разделение ответственности**: API клиент отделен от тестов
2. **Переиспользование кода**: Один универсальный клиент для всех запросов
3. **Управление тестовыми данными**: Генераторы и фикстуры для создания/очистки
4. **Логирование**: Детальное логирование всех запросов/ответов
5. **Обработка ошибок**: Централизованная обработка в клиенте
6. **Чистота тестов**: Автоматическая очистка созданных данных через фикстуры
7. **Параметризация**: Использование `@pytest.mark.parametrize` для множественных сценариев
8. **Маркеры**: Организация тестов по типам (positive, negative) и API (pet, store, user)

## Примеры использования

### Создание клиента с базовым путем
```python
from api.client import APIClient

# Клиент для работы с Pet API (базовый путь /pet)
pet_client = APIClient(base_path='/pet')

# Теперь все запросы будут идти к /pet/*
response = pet_client.post(json_data=pet_data)  # POST /pet
response = pet_client.get('/123')  # GET /pet/123
response = pet_client.get('/findByStatus', params={'status': 'available'})  # GET /pet/findByStatus?status=available
```

### Использование в тестах
```python
def test_create_pet(pet_client, pet_data):
    # pet_client уже имеет базовый путь /pet
    response = pet_client.post(json_data=pet_data)  # POST /pet
    assert response.status_code == 200

def test_get_pet(pet_client, created_pet):
    pet_id = created_pet['id']
    response = pet_client.get(f"/{pet_id}")  # GET /pet/{id}
    assert response.status_code == 200

def test_find_pets_by_status(pet_client):
    response = pet_client.get('/findByStatus', params={'status': 'available'})  # GET /pet/findByStatus?status=available
    assert response.status_code == 200
```

### Работа с разными API
```python
# Pet API
pet_client = APIClient(base_path='/pet')
pet_client.post(json_data=pet_data)  # POST /pet
pet_client.get('/123')  # GET /pet/123

# Store API
store_client = APIClient(base_path='/store')
store_client.post('/order', json_data=order_data)  # POST /store/order
store_client.get('/inventory')  # GET /store/inventory

# User API
user_client = APIClient(base_path='/user')
user_client.post(json_data=user_data)  # POST /user
user_client.get('/login', params={'username': 'user', 'password': 'pass'})  # GET /user/login?username=user&password=pass
```