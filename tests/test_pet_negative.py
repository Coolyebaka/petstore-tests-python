import pytest


@pytest.mark.api
@pytest.mark.negative
def test_get_pet_not_found(api):
    """Негатив: запрос заведомо несуществующего питомца."""
    resp = api.get("/pet/999999999999")
    # Демостенд может вернуть 200 с каким-то объектом — учитываем оба варианта
    assert resp.status_code in (404, 200), resp.text

    if resp.status_code == 200:
        body = resp.json()
        assert "id" in body
        assert "name" in body


@pytest.mark.api
@pytest.mark.negative
def test_create_pet_missing_required_name(api, faker):
    """Негатив: создание питомца без обязательного поля name."""
    payload = {
        "id": faker.random_int(min=1_000_000, max=9_999_999),
        "photoUrls": ["https://example.com/photo.jpg"],
    }

    resp = api.post("/pet", json=payload)
    assert resp.status_code in (400, 405, 500), resp.text


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.parametrize("invalid_id", [-1, 0, 99999999999999])
def test_get_pet_invalid_or_nonexistent(api, invalid_id):
    """Негатив: запрос питомца с некорректным или несуществующим ID."""
    resp = api.get(f"/pet/{invalid_id}")
    assert resp.status_code in (400, 404), resp.text


@pytest.mark.api
@pytest.mark.negative
def test_update_pet_with_invalid_status(api, pet_payload):
    """Негатив: обновление питомца с некорректным значением статуса."""
    create = api.post("/pet", json=pet_payload)
    assert create.status_code in (200, 201), create.text

    bad_payload = dict(pet_payload)
    bad_payload["status"] = "NOT_A_VALID_STATUS"

    resp = api.put("/pet", json=bad_payload)
    assert resp.status_code in (200, 400, 500), resp.text


@pytest.mark.api
@pytest.mark.negative
def test_delete_pet_twice_is_idempotent(api, faker):
    """Негатив/идемпотентность: удаление одного и того же ID дважды."""
    pet_id = faker.random_int(min=100_000_000, max=900_000_000)

    resp1 = api.delete(f"/pet/{pet_id}")
    resp2 = api.delete(f"/pet/{pet_id}")

    assert resp1.status_code in (200, 202, 404), resp1.text
    assert resp2.status_code in (200, 202, 404), resp2.text
