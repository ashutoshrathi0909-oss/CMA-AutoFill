"""Tests for client CRUD endpoints."""
from fastapi.testclient import TestClient
from uuid import uuid4
from tests.conftest import TEST_FIRM_ID, make_client_row


def test_create_client_success(authed_client: TestClient, mock_db):
    row = make_client_row()
    mock_db.set_table("clients", data=[row])
    mock_db.set_table("audit_log", data=[{}])

    res = authed_client.post("/api/v1/clients", json={
        "name": "Test Corp",
        "entity_type": "trading",
    })
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["name"] == "Test Corp"
    assert data["entity_type"] == "trading"
    assert data["cma_count"] == 0


def test_create_client_invalid_entity_type(authed_client: TestClient):
    res = authed_client.post("/api/v1/clients", json={
        "name": "Test",
        "entity_type": "invalid_type",
    })
    assert res.status_code == 422


def test_create_client_missing_name(authed_client: TestClient):
    res = authed_client.post("/api/v1/clients", json={
        "entity_type": "trading",
    })
    assert res.status_code == 422


def test_create_client_no_auth(unauthed_client: TestClient):
    res = unauthed_client.post("/api/v1/clients", json={
        "name": "Test",
        "entity_type": "trading",
    })
    assert res.status_code == 401


def test_list_clients_success(authed_client: TestClient, mock_db):
    rows = [make_client_row(name="Client A"), make_client_row(name="Client B")]
    mock_db.set_table("clients", data=rows, count=2)
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.get("/api/v1/clients")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 20


def test_list_clients_empty(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)

    res = authed_client.get("/api/v1/clients")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] == 0
    assert data["items"] == []


def test_list_clients_pagination_params(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.get("/api/v1/clients?page=2&per_page=5")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["page"] == 2
    assert data["per_page"] == 5


def test_get_client_success(authed_client: TestClient, mock_db):
    client_id = str(uuid4())
    row = make_client_row(client_id=client_id)
    mock_db.set_table("clients", data=[row])
    mock_db.set_table("cma_projects", data=[], count=0)

    res = authed_client.get(f"/api/v1/clients/{client_id}")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == client_id


def test_get_client_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[])

    res = authed_client.get("/api/v1/clients/nonexistent-id")
    assert res.status_code == 404


def test_update_client_success(authed_client: TestClient, mock_db):
    client_id = str(uuid4())
    row = make_client_row(client_id=client_id)
    updated_row = {**row, "name": "Updated Corp"}
    mock_db.set_table("clients", data=[row])
    mock_db.set_table("audit_log", data=[{}])
    mock_db.set_table("cma_projects", data=[], count=0)

    res = authed_client.put(f"/api/v1/clients/{client_id}", json={
        "name": "Updated Corp",
    })
    assert res.status_code == 200


def test_update_client_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[])

    res = authed_client.put("/api/v1/clients/nonexistent", json={"name": "X"})
    assert res.status_code == 404


def test_delete_client_success(authed_client: TestClient, mock_db):
    client_id = str(uuid4())
    row = make_client_row(client_id=client_id)
    mock_db.set_table("clients", data=[row])
    mock_db.set_table("audit_log", data=[{}])

    res = authed_client.delete(f"/api/v1/clients/{client_id}")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["success"] is True


def test_delete_client_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[])

    res = authed_client.delete("/api/v1/clients/nonexistent")
    assert res.status_code == 404


def test_response_follows_standard_format(authed_client: TestClient, mock_db):
    row = make_client_row()
    mock_db.set_table("clients", data=[row])
    mock_db.set_table("audit_log", data=[{}])

    res = authed_client.post("/api/v1/clients", json={
        "name": "Test", "entity_type": "service",
    })
    body = res.json()
    assert "data" in body
    assert "error" in body
