from typing import Any, Dict, List, Optional

import requests


def validate_status_code(response: requests.Response, expected_code: int) -> bool:
    assert response.status_code == expected_code, (
        f"Expected status code {expected_code}, but got {response.status_code}. "
        f"Response: {response.text}"
    )
    return True


def validate_response_time(response: requests.Response, max_time: float = 5.0) -> bool:
    elapsed = response.elapsed.total_seconds()
    assert elapsed <= max_time, (
        f"Response time {elapsed:.2f}s exceeds maximum {max_time}s"
    )
    return True


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    missing_fields = [field for field in required_fields if field not in data]
    assert not missing_fields, (
        f"Missing required fields: {', '.join(missing_fields)}. "
        f"Available fields: {', '.join(data.keys())}"
    )
    return True


def validate_pet_data(pet_data: Dict[str, Any]) -> bool:
    required_fields = ["id", "name", "status"]
    validate_json_structure(pet_data, required_fields)

    assert isinstance(pet_data["id"], int), "Pet ID must be an integer"
    assert isinstance(pet_data["name"], str), "Pet name must be a string"
    assert pet_data["status"] in ["available", "pending", "sold"], (
        f"Invalid status: {pet_data['status']}"
    )

    return True


def validate_user_data(user_data: Dict[str, Any]) -> bool:
    required_fields = ["id", "username"]
    validate_json_structure(user_data, required_fields)

    assert isinstance(user_data["id"], int), "User ID must be an integer"
    assert isinstance(user_data["username"], str), "Username must be a string"

    return True


def validate_order_data(order_data: Dict[str, Any]) -> bool:
    required_fields = ["id", "petId", "quantity", "status"]
    validate_json_structure(order_data, required_fields)

    assert isinstance(order_data["id"], int), "Order ID must be an integer"
    assert isinstance(order_data["petId"], int), "Pet ID must be an integer"
    assert isinstance(order_data["quantity"], int), "Quantity must be an integer"
    assert order_data["status"] in ["placed", "approved", "delivered"], (
        f"Invalid order status: {order_data['status']}"
    )

    return True


def validate_error_response(
    response: requests.Response, expected_message: Optional[str] = None
) -> bool:
    assert 400 <= response.status_code < 500, (
        f"Expected error status code (4xx), but got {response.status_code}"
    )

    if expected_message:
        response_data = (
            response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else {}
        )
        if "message" in response_data:
            assert expected_message.lower() in response_data["message"].lower(), (
                f"Expected error message containing '{expected_message}', "
                f"but got '{response_data.get('message', '')}'"
            )

    return True
