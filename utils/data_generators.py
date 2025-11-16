from typing import Any, Dict, List

from faker import Faker

fake = Faker()


def generate_pet_data(
    pet_id: int = None,
    name: str = None,
    status: str = "available",
    category_id: int = None,
    category_name: str = None,
    tags: List[Dict[str, Any]] = None,
    photo_urls: List[str] = None,
) -> Dict[str, Any]:
    if pet_id is None:
        pet_id = fake.random_int(min=1, max=999999)

    if name is None:
        name = fake.first_name()

    pet_data = {"id": pet_id, "name": name, "status": status}

    if category_id is not None or category_name is not None:
        pet_data["category"] = {
            "id": category_id or fake.random_int(min=1, max=100),
            "name": category_name or fake.word().capitalize(),
        }

    if tags is not None:
        pet_data["tags"] = tags
    else:
        pet_data["tags"] = [
            {"id": fake.random_int(min=1, max=100), "name": fake.word()}
        ]

    if photo_urls is not None:
        pet_data["photoUrls"] = photo_urls
    else:
        pet_data["photoUrls"] = [fake.image_url()]

    return pet_data


def generate_user_data(
    user_id: int = None,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    password: str = None,
    phone: str = None,
    user_status: int = 0,
) -> Dict[str, Any]:
    if user_id is None:
        user_id = fake.random_int(min=1, max=999999)

    if username is None:
        username = fake.user_name()

    if first_name is None:
        first_name = fake.first_name()

    if last_name is None:
        last_name = fake.last_name()

    if email is None:
        email = fake.email()

    if password is None:
        password = fake.password(length=12)

    if phone is None:
        phone = fake.phone_number()

    return {
        "id": user_id,
        "username": username,
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "password": password,
        "phone": phone,
        "userStatus": user_status,
    }


def generate_order_data(
    order_id: int = None,
    pet_id: int = None,
    quantity: int = 1,
    ship_date: str = None,
    status: str = "placed",
    complete: bool = False,
) -> Dict[str, Any]:
    if order_id is None:
        order_id = fake.random_int(min=1, max=999999)

    if pet_id is None:
        pet_id = fake.random_int(min=1, max=999999)

    if ship_date is None:
        ship_date = fake.iso8601()

    return {
        "id": order_id,
        "petId": pet_id,
        "quantity": quantity,
        "shipDate": ship_date,
        "status": status,
        "complete": complete,
    }


def generate_users_list(count: int = 3) -> List[Dict[str, Any]]:
    return [generate_user_data() for _ in range(count)]
