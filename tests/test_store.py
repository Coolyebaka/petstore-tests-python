import pytest

from api.client import APIClient
from utils.data_generators import generate_order_data
from utils.retries import retry_until_condition
from utils.validators import (
    validate_error_response,
    validate_order_data,
    validate_status_code,
)


@pytest.mark.api
@pytest.mark.store
class TestStoreAPI:
    @pytest.mark.positive
    def test_place_order(self, store_client: APIClient, order_data: dict):
        response = store_client.post("/order", json_data=order_data)

        validate_status_code(response, 200)
        created_order = response.json()
        validate_order_data(created_order)

        assert created_order["id"] == order_data["id"]
        assert created_order["petId"] == order_data["petId"]
        assert created_order["quantity"] == order_data["quantity"]

    @pytest.mark.positive
    def test_get_order_by_id(self, store_client: APIClient, created_order: dict):
        order_id = created_order["id"]
        response = store_client.get(f"/order/{order_id}", retry_on_404=True)

        validate_status_code(response, 200)
        order = response.json()
        validate_order_data(order)

        assert order["id"] == order_id
        assert order["petId"] == created_order["petId"]

    @pytest.mark.positive
    def test_delete_order(self, store_client: APIClient, order_data: dict):
        create_response = store_client.post("/order", json_data=order_data)
        order_id = create_response.json()["id"]

        delete_response = store_client.delete(f"/order/{order_id}", retry_on_404=True)
        validate_status_code(delete_response, 200)

        get_response = store_client.get(f"/order/{order_id}", expected_status=None)
        validate_status_code(get_response, 404)

    @pytest.mark.positive
    def test_get_inventory(self, store_client: APIClient):
        response = store_client.get("/inventory")

        validate_status_code(response, 200)
        inventory = response.json()

        assert isinstance(inventory, dict)
        for status in ["available", "pending", "sold"]:
            if status in inventory:
                assert isinstance(inventory[status], int)
                assert inventory[status] >= 0

    @pytest.mark.negative
    def test_get_nonexistent_order(self, store_client: APIClient):
        nonexistent_id = 999999999
        response = store_client.get(f"/order/{nonexistent_id}", expected_status=None)

        validate_status_code(response, 404)
        validate_error_response(response)

    @pytest.mark.negative
    def test_delete_nonexistent_order(self, store_client: APIClient):
        nonexistent_id = 999999999
        response = store_client.delete(f"/order/{nonexistent_id}", expected_status=None)

        assert response.status_code in [200, 404]

    @pytest.mark.negative
    def test_place_order_invalid_data(self, store_client: APIClient):
        invalid_data = {
            "id": "not_an_integer",
            "petId": -1,
            "quantity": -1,
            "status": "invalid_status",
        }

        response = store_client.post(
            "/order", json_data=invalid_data, expected_status=None
        )

        assert response.status_code >= 400

    @pytest.mark.parametrize("status", ["placed", "approved", "delivered"])
    def test_order_with_different_statuses(self, store_client: APIClient, status: str):
        order_data = generate_order_data(status=status)

        response = store_client.post("/order", json_data=order_data)
        validate_status_code(response, 200)

        created_order = response.json()
        assert created_order["status"] == status

        store_client.delete(f"/order/{created_order['id']}", expected_status=None)

    def test_order_lifecycle(self, store_client: APIClient, order_data: dict):
        create_response = store_client.post("/order", json_data=order_data)
        validate_status_code(create_response, 200)
        created_order = create_response.json()
        order_id = created_order["id"]

        get_response = store_client.get(f"/order/{order_id}", retry_on_404=True)
        validate_status_code(get_response, 200)
        retrieved_order = get_response.json()
        assert retrieved_order["id"] == order_id

        delete_response = store_client.delete(f"/order/{order_id}", retry_on_404=True)
        validate_status_code(delete_response, 200)

        get_after_delete = retry_until_condition(
            operation=lambda: store_client.get(
                f"/order/{order_id}", expected_status=None
            ),
            condition=lambda response: response.status_code == 404,
            error_message=f"Order {order_id} was not deleted after DELETE request",
        )
        validate_status_code(get_after_delete, 404)
