"""Tests for CMA project CRUD endpoints."""
from fastapi.testclient import TestClient
from tests.conftest import TEST_FIRM_ID, TEST_USER_ID, make_project_row, make_client_row
from uuid import uuid4


def _client_row():
    return make_client_row(client_id=str(uuid4()))


def test_create_project_success(authed_client: TestClient, mock_db):
    """Create project: mock returns empty for duplicate check, then row for insert.
    Since our simple MockQueryBuilder returns the same data for all calls to a table,
    we use a side-effect approach by patching the endpoint's get_supabase.
    """
    from unittest.mock import MagicMock, patch

    client_id = str(uuid4())
    client_row = make_client_row(client_id=client_id)
    project_row = make_project_row(client_id=client_id)

    # Build a mock db where cma_projects table returns different results per call
    db = MagicMock()

    # clients table — always returns the client
    clients_table = MagicMock()
    clients_result = MagicMock()
    clients_result.data = [client_row]
    clients_table.select.return_value = clients_table
    clients_table.eq.return_value = clients_table
    clients_table.execute.return_value = clients_result

    # cma_projects table — first call (duplicate check) returns empty, second call (insert) returns row
    cma_table = MagicMock()
    empty_result = MagicMock()
    empty_result.data = []
    insert_result = MagicMock()
    insert_result.data = [project_row]
    cma_table.select.return_value = cma_table
    cma_table.eq.return_value = cma_table
    cma_table.insert.return_value = cma_table
    cma_table.execute.side_effect = [empty_result, insert_result]

    # audit_log table
    audit_table = MagicMock()
    audit_result = MagicMock()
    audit_result.data = [{}]
    audit_table.insert.return_value = audit_table
    audit_table.execute.return_value = audit_result

    def table_router(name):
        if name == "clients":
            return clients_table
        if name == "cma_projects":
            return cma_table
        if name == "audit_log":
            return audit_table
        return MagicMock()

    db.table.side_effect = table_router

    with patch("app.api.v1.endpoints.projects.get_supabase", return_value=db):
        res = authed_client.post("/api/v1/projects", json={
            "client_id": client_id,
            "financial_year": "2024-25",
        })

    assert res.status_code == 201
    data = res.json()["data"]
    assert data["financial_year"] == "2024-25"
    assert data["status"] == "draft"


def test_create_project_invalid_financial_year(authed_client: TestClient):
    res = authed_client.post("/api/v1/projects", json={
        "client_id": str(uuid4()),
        "financial_year": "2024",  # Invalid format, should be YYYY-YY
    })
    assert res.status_code == 422


def test_create_project_no_auth(unauthed_client: TestClient):
    res = unauthed_client.post("/api/v1/projects", json={
        "client_id": str(uuid4()),
        "financial_year": "2024-25",
    })
    assert res.status_code == 401


def test_create_project_client_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[])  # No client found

    res = authed_client.post("/api/v1/projects", json={
        "client_id": str(uuid4()),
        "financial_year": "2024-25",
    })
    assert res.status_code == 404


def test_list_projects_success(authed_client: TestClient, mock_db):
    proj = make_project_row()
    proj["clients"] = {"name": "Test Corp", "entity_type": "trading"}
    mock_db.set_table("cma_projects", data=[proj], count=1)

    res = authed_client.get("/api/v1/projects")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_list_projects_empty(authed_client: TestClient, mock_db):
    mock_db.set_table("cma_projects", data=[], count=0)

    res = authed_client.get("/api/v1/projects")
    assert res.status_code == 200
    assert res.json()["data"]["items"] == []


def test_get_project_success(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id)
    proj["clients"] = {"name": "Test Corp", "entity_type": "trading"}
    mock_db.set_table("cma_projects", data=[proj])
    mock_db.set_table("uploaded_files", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)

    res = authed_client.get(f"/api/v1/projects/{proj_id}")
    assert res.status_code == 200
    assert res.json()["data"]["id"] == proj_id


def test_get_project_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.get(f"/api/v1/projects/{uuid4()}")
    assert res.status_code == 404


def test_update_project_non_draft_rejected(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="extracting")
    mock_db.set_table("cma_projects", data=[proj])

    res = authed_client.put(f"/api/v1/projects/{proj_id}", json={
        "bank_name": "SBI",
    })
    assert res.status_code == 409
    assert "Cannot modify" in res.json()["detail"]


def test_update_project_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.put(f"/api/v1/projects/{uuid4()}", json={"bank_name": "SBI"})
    assert res.status_code == 404


def test_delete_project_draft_success(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="draft")
    mock_db.set_table("cma_projects", data=[proj])
    mock_db.set_table("audit_log", data=[{}])

    res = authed_client.delete(f"/api/v1/projects/{proj_id}")
    assert res.status_code == 200
    assert res.json()["data"]["success"] is True


def test_delete_project_non_draft_rejected(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="completed")
    mock_db.set_table("cma_projects", data=[proj])

    res = authed_client.delete(f"/api/v1/projects/{proj_id}")
    assert res.status_code == 409
    assert "Cannot delete" in res.json()["detail"]


def test_delete_project_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.delete(f"/api/v1/projects/{uuid4()}")
    assert res.status_code == 404
