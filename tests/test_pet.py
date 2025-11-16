import pytest

from api.client import APIClient
from utils.data_generators import generate_pet_data
from utils.retries import retry_until_condition
from utils.validators import (
    validate_error_response,
    validate_pet_data,
    validate_status_code,
)


@pytest.mark.api
@pytest.mark.pet
class TestPetAPI:
    @pytest.mark.positive
    def test_create_pet(self, pet_client: APIClient, pet_data: dict):
        response = pet_client.post(json_data=pet_data)

        validate_status_code(response, 200)
        created_pet = response.json()
        validate_pet_data(created_pet)

        assert created_pet["id"] == pet_data["id"]
        assert created_pet["name"] == pet_data["name"]
        assert created_pet["status"] == pet_data["status"]

    @pytest.mark.positive
    def test_get_pet_by_id(self, pet_client: APIClient, created_pet: dict):
        pet_id = created_pet["id"]
        response = pet_client.get(f"/{pet_id}", retry_on_404=True)

        validate_status_code(response, 200)
        pet = response.json()
        validate_pet_data(pet)

        assert pet["id"] == pet_id
        assert pet["name"] == created_pet["name"]

    @pytest.mark.positive
    def test_update_pet(self, pet_client: APIClient, created_pet: dict):
        updated_data = created_pet.copy()
        updated_data["name"] = "Updated Pet Name"
        updated_data["status"] = "sold"

        response = pet_client.put(json_data=updated_data)

        validate_status_code(response, 200)
        updated_pet = response.json()
        validate_pet_data(updated_pet)

        assert updated_pet["name"] == "Updated Pet Name"
        assert updated_pet["status"] == "sold"

    @pytest.mark.positive
    def test_update_pet_form_data(self, pet_client: APIClient, created_pet: dict):
        pet_id = created_pet["id"]
        new_name = "Form Updated Name"
        new_status = "pending"

        data = {"name": new_name, "status": new_status}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = pet_client.post(
            f"/{pet_id}", data=data, headers=headers, retry_on_404=True
        )

        validate_status_code(response, 200)

        get_response = pet_client.get(f"/{pet_id}", retry_on_404=True)
        updated_pet = get_response.json()
        assert updated_pet["name"] == new_name
        assert updated_pet["status"] == new_status

    @pytest.mark.positive
    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_find_pets_by_status(self, pet_client: APIClient, status: str):
        response = pet_client.get("/findByStatus", params={"status": status})

        validate_status_code(response, 200)
        pets = response.json()

        assert isinstance(pets, list)
        for pet in pets:
            assert pet["status"] == status

    @pytest.mark.positive
    def test_delete_pet(self, pet_client: APIClient, pet_data: dict):
        create_response = pet_client.post(json_data=pet_data)
        pet_id = create_response.json()["id"]

        delete_response = pet_client.delete(f"/{pet_id}", retry_on_404=True)
        validate_status_code(delete_response, 200)

        get_response = pet_client.get(f"/{pet_id}", expected_status=None)
        validate_status_code(get_response, 404)

    @pytest.mark.negative
    def test_get_nonexistent_pet(self, pet_client: APIClient):
        nonexistent_id = 999999999
        response = pet_client.get(f"/{nonexistent_id}", expected_status=None)

        validate_status_code(response, 404)
        validate_error_response(response)

    @pytest.mark.negative
    def test_delete_nonexistent_pet(self, pet_client: APIClient):
        nonexistent_id = 999999999
        response = pet_client.delete(f"/{nonexistent_id}", expected_status=None)

        assert response.status_code in [200, 404]

    @pytest.mark.negative
    def test_create_pet_invalid_data(self, pet_client: APIClient):
        invalid_data = {"id": "not_an_integer", "name": "", "status": "invalid_status"}

        response = pet_client.post(json_data=invalid_data, expected_status=None)

        assert response.status_code >= 400

    @pytest.mark.negative
    def test_update_pet_invalid_id(self, pet_client: APIClient):
        invalid_pet_data = generate_pet_data(
            pet_id="not_an_integer", name="Invalid Pet"
        )

        response = pet_client.put(json_data=invalid_pet_data, expected_status=None)

        assert response.status_code >= 400

    def test_pet_lifecycle(self, pet_client: APIClient, pet_data: dict):
        create_response = pet_client.post(json_data=pet_data)
        validate_status_code(create_response, 200)
        created_pet = create_response.json()
        pet_id = created_pet["id"]

        updated_data = created_pet.copy()
        updated_data["status"] = "sold"
        update_response = pet_client.put(json_data=updated_data, retry_on_404=False)
        validate_status_code(update_response, 200)

        delete_response = pet_client.delete(f"/{pet_id}", retry_on_404=True)
        validate_status_code(delete_response, 200)

        get_after_delete = retry_until_condition(
            operation=lambda: pet_client.get(f"/{pet_id}", expected_status=None),
            condition=lambda response: response.status_code == 404,
            error_message=f"Pet {pet_id} was not deleted after DELETE request",
        )
        validate_status_code(get_after_delete, 404)
