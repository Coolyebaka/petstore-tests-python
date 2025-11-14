import pytest


@pytest.mark.api
@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_find_by_status_returns_only_requested_status(api, status):
    """Позитив: поиск по каждому статусу возвращает только этот статус (на выборке)."""
    resp = api.get("/pet/findByStatus", params={"status": status})
    assert resp.status_code == 200, resp.text

    items = resp.json()
    for pet in items[:50]:
        assert pet.get("status") == status


@pytest.mark.api
def test_find_by_status_multiple_values(api):
    """Позитив: поиск по нескольким статусам сразу (через запятую)."""
    statuses = "available,pending"
    resp = api.get("/pet/findByStatus", params={"status": statuses})
    assert resp.status_code == 200, resp.text

    items = resp.json()
    allowed = {"available", "pending"}

    for pet in items[:50]:
        assert pet.get("status") in allowed
