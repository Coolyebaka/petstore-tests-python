import pytest

from api.client import APIClient
from utils.retries import retry_until_condition
from utils.validators import (
    validate_error_response,
    validate_status_code,
    validate_user_data,
)


@pytest.mark.api
@pytest.mark.user
class TestUserAPI:
    @pytest.mark.positive
    def test_create_user(self, user_client: APIClient, user_data: dict):
        response = user_client.post(json_data=user_data)

        validate_status_code(response, 200)

    @pytest.mark.positive
    def test_get_user_by_username(self, user_client: APIClient, created_user: dict):
        username = created_user["username"]
        response = user_client.get(f"/{username}", retry_on_404=True)

        validate_status_code(response, 200)
        user = response.json()
        validate_user_data(user)

        assert user["username"] == username
        assert user["id"] == created_user["id"]

    @pytest.mark.positive
    def test_update_user(self, user_client: APIClient, created_user: dict):
        updated_data = created_user.copy()
        updated_data["firstName"] = "Updated First Name"
        updated_data["lastName"] = "Updated Last Name"

        response = user_client.put(
            f"/{created_user['username']}", json_data=updated_data
        )
        validate_status_code(response, 200)

    @pytest.mark.positive
    def test_delete_user(self, user_client: APIClient, user_data: dict):
        create_response = user_client.post(json_data=user_data)
        validate_status_code(create_response, 200)

        delete_response = user_client.delete(
            f"/{user_data['username']}", retry_on_404=True
        )
        validate_status_code(delete_response, 200)

        get_response = user_client.get(
            f"/{user_data['username']}", expected_status=None
        )
        validate_status_code(get_response, 404)

    @pytest.mark.positive
    def test_user_login(self, user_client: APIClient, created_user: dict):
        response = user_client.get(
            "/login",
            params={
                "username": created_user["username"],
                "password": created_user["password"],
            },
        )

        validate_status_code(response, 200)
        response_data = response.json()

        assert "message" in response_data or "code" in response_data

    @pytest.mark.positive
    def test_user_logout(self, user_client: APIClient):
        response = user_client.get("/logout")

        validate_status_code(response, 200)
        response_data = response.json()

        assert "message" in response_data or "code" in response_data

    @pytest.mark.positive
    def test_create_users_with_list(self, user_client: APIClient, users_list: list):
        response = user_client.post("/createWithList", json_data=users_list)

        validate_status_code(response, 200)

        for user in users_list:
            get_response = user_client.get(f"/{user['username']}", retry_on_404=True)
            validate_status_code(get_response, 200)
            retrieved_user = get_response.json()
            assert retrieved_user["username"] == user["username"]

        for user in users_list:
            try:
                user_client.delete(
                    f"/{user['username']}", expected_status=None, retry_on_404=True
                )
            except Exception:
                pass

    @pytest.mark.negative
    def test_get_nonexistent_user(self, user_client: APIClient):
        nonexistent_username = "nonexistent_user_999999"
        response = user_client.get(f"/{nonexistent_username}", expected_status=None)

        validate_status_code(response, 404)
        validate_error_response(response)

    @pytest.mark.negative
    def test_delete_nonexistent_user(self, user_client: APIClient):
        nonexistent_username = "nonexistent_user_999999"
        response = user_client.delete(f"/{nonexistent_username}", expected_status=None)

        assert response.status_code in [200, 404]

    @pytest.mark.negative
    def test_create_user_invalid_data(self, user_client: APIClient):
        invalid_data = {
            "id": "not_an_integer",
            "username": "",
            "email": "invalid_email",
        }

        response = user_client.post(json_data=invalid_data, expected_status=None)

        assert response.status_code >= 400

    def test_user_lifecycle(self, user_client: APIClient, user_data: dict):
        create_response = user_client.post(json_data=user_data)
        validate_status_code(create_response, 200)

        get_response = user_client.get(f"/{user_data['username']}", retry_on_404=True)
        validate_status_code(get_response, 200)
        retrieved_user = get_response.json()
        assert retrieved_user["username"] == user_data["username"]

        updated_data = user_data.copy()
        updated_data["firstName"] = "Updated Name"
        update_response = user_client.put(
            f"/{user_data['username']}", json_data=updated_data
        )
        validate_status_code(update_response, 200)

        delete_response = user_client.delete(
            f"/{user_data['username']}", retry_on_404=True
        )
        validate_status_code(delete_response, 200)

        get_after_delete = retry_until_condition(
            operation=lambda: user_client.get(
                f"/{user_data['username']}", expected_status=None
            ),
            condition=lambda response: response.status_code == 404,
            error_message=f"User {user_data['username']} was not deleted after DELETE request",
        )
        validate_status_code(get_after_delete, 404)

    def test_user_login_logout_flow(self, user_client: APIClient, created_user: dict):
        login_response = user_client.get(
            "/login",
            params={
                "username": created_user["username"],
                "password": created_user["password"],
            },
        )
        validate_status_code(login_response, 200)

        logout_response = user_client.get("/logout")
        validate_status_code(logout_response, 200)
