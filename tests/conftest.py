import os
import uuid
from typing import Callable, Dict

import pytest
from faker import Faker

from src.api_client import ApiClient


@pytest.fixture(scope="session")
def api() -> ApiClient:
    """Экземпляр ApiClient на всю сессию тестов."""
    base_url = os.getenv("PETSTORE_BASE_URL")
    return ApiClient(base_url=base_url)


@pytest.fixture(scope="session")
def faker() -> Faker:
    """Один Faker на все тесты."""
    return Faker()


@pytest.fixture
def unique_pet_id() -> int:
    """Генерируем большой уникальный ID на основе UUID."""
    return int(uuid.uuid4().int % 10**9)


@pytest.fixture
def pet_payload(unique_pet_id: int, faker: Faker) -> Dict:
    """Базовый позитивный payload для питомца."""
    return {
        "id": unique_pet_id,
        "name": faker.first_name(),
        "status": "available",
        "photoUrls": [faker.image_url()],
        "category": {"id": 1, "name": faker.word()},
        "tags": [{"id": 1, "name": faker.word()}],
    }


@pytest.fixture
def pet_factory(api: ApiClient, faker: Faker) -> Callable[..., Dict]:
    """Фабрика: создаёт питомца через API и возвращает payload."""

    def _create_pet(**overrides: object) -> Dict:
        payload: Dict[str, object] = {
            "id": int(uuid.uuid4().int % 10**9),
            "name": faker.first_name(),
            "status": "available",
            "photoUrls": [faker.image_url()],
            "category": {"id": 1, "name": faker.word()},
            "tags": [{"id": 1, "name": faker.word()}],
        }
        payload.update(overrides)

        resp = api.post("/pet", json=payload)
        assert resp.status_code in (200, 201), resp.text
        return payload

    return _create_pet
