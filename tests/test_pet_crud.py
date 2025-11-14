import time

import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_create_get_update_delete_pet_full_flow(api, pet_payload):
    """Полный позитивный сценарий CRUD для /pet."""
    # Create
    create_resp = api.post("/pet", json=pet_payload)
    assert create_resp.status_code in (200, 201), create_resp.text

    pet_id = pet_payload["id"]

    # Poll until created — Petstore иногда отвечает не сразу 200
    def try_get():
        resp = api.get(f"/pet/{pet_id}")
        print(f"[GET] status={resp.status_code} text={resp.text[:200]}")
        return resp

    for _ in range(5):
        get_resp = try_get()
        if get_resp.status_code == 200:
            break
        time.sleep(0.3)
    else:
        # последний шанс — пересоздать и проверить
        recreate = api.post("/pet", json=pet_payload)
        assert recreate.status_code in (200, 201), recreate.text
        get_resp = try_get()
        assert get_resp.status_code == 200, get_resp.text

    body = get_resp.json()
    assert body["id"] == pet_id
    assert body["name"] == pet_payload["name"]
    assert body["status"] == pet_payload["status"]

    # Update via PUT
    updated_payload = dict(pet_payload)
    updated_payload["name"] += "-updated"
    updated_payload["status"] = "sold"

    updated_resp = api.put("/pet", json=updated_payload)
    assert updated_resp.status_code == 200, updated_resp.text

    updated_body = updated_resp.json()
    assert updated_body["id"] == pet_id
    assert updated_body["name"] == updated_payload["name"]
    assert updated_body["status"] == "sold"

    # Delete
    deleted_resp = api.delete(f"/pet/{pet_id}")
    # Демостенд может вернуть 404, если кто-то уже удалил — учитываем это
    assert deleted_resp.status_code in (200, 202, 404), (
        f"[DELETE] expected 200/202/404, got {deleted_resp.status_code}: {deleted_resp.text}"
    )

    # Доп. проверка: питомец больше недоступен
    final_get = api.get(f"/pet/{pet_id}")
    assert final_get.status_code in (404, 410), final_get.text
