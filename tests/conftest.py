from typing import Any, Dict, Generator, List

import pytest

from api.client import APIClient
from utils.data_generators import (
    generate_order_data,
    generate_pet_data,
    generate_user_data,
    generate_users_list,
)


@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def pet_client() -> Generator[APIClient, None, None]:
    client = APIClient(base_path="/pet")
    yield client
    client.close()


@pytest.fixture(scope="session")
def store_client() -> Generator[APIClient, None, None]:
    client = APIClient(base_path="/store")
    yield client
    client.close()


@pytest.fixture(scope="session")
def user_client() -> Generator[APIClient, None, None]:
    client = APIClient(base_path="/user")
    yield client
    client.close()


@pytest.fixture
def pet_data() -> Dict[str, Any]:
    return generate_pet_data()


@pytest.fixture
def user_data() -> Dict[str, Any]:
    return generate_user_data()


@pytest.fixture
def order_data() -> Dict[str, Any]:
    return generate_order_data()


@pytest.fixture
def users_list() -> List[Dict[str, Any]]:
    return generate_users_list(3)


@pytest.fixture
def created_pet(
    pet_client: APIClient, pet_data: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    response = pet_client.post(json_data=pet_data)
    assert response.status_code == 200, f"Failed to create pet: {response.text}"
    created_pet_data = response.json()

    yield created_pet_data

    try:
        pet_client.delete(f"/{created_pet_data['id']}", expected_status=None)
    except Exception:
        pass


@pytest.fixture
def created_user(
    user_client: APIClient, user_data: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    response = user_client.post(json_data=user_data)
    assert response.status_code == 200, f"Failed to create user: {response.text}"

    yield user_data

    try:
        user_client.delete(f"/{user_data['username']}", expected_status=None)
    except Exception:
        pass


@pytest.fixture
def created_order(
    store_client: APIClient, order_data: Dict[str, Any]
) -> Generator[Dict[str, Any], None, None]:
    response = store_client.post("/order", json_data=order_data)
    assert response.status_code == 200, f"Failed to create order: {response.text}"
    created_order_data = response.json()

    yield created_order_data

    try:
        store_client.delete(f"/order/{created_order_data['id']}", expected_status=None)
    except Exception:
        pass
