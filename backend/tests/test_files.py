"""Tests for file upload/download endpoints."""
import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.conftest import TEST_FIRM_ID, make_project_row, make_file_row
from uuid import uuid4


def test_upload_file_success(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="draft")
    file_row = make_file_row()

    mock_db.set_table("cma_projects", data=[proj])
    mock_db.set_table("uploaded_files", data=[file_row])
    mock_db.set_table("audit_log", data=[{}])

    with patch("app.api.v1.endpoints.files.upload_file", return_value="fake/path.xlsx"):
        res = authed_client.post(
            f"/api/v1/projects/{proj_id}/files",
            files={"file": ("test.xlsx", b"fake content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            data={"document_type": "balance_sheet"},
        )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["file_name"] == "test.xlsx"
    assert data["extraction_status"] == "pending"


def test_upload_file_invalid_extension(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="draft")
    mock_db.set_table("cma_projects", data=[proj])

    res = authed_client.post(
        f"/api/v1/projects/{proj_id}/files",
        files={"file": ("doc.docx", b"fake", "application/msword")},
    )
    assert res.status_code == 422
    assert "not supported" in res.json()["detail"]


def test_upload_file_too_large(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="draft")
    mock_db.set_table("cma_projects", data=[proj])

    big_content = b"x" * (11 * 1024 * 1024)  # 11MB
    res = authed_client.post(
        f"/api/v1/projects/{proj_id}/files",
        files={"file": ("big.xlsx", big_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert res.status_code == 413
    assert "10MB" in res.json()["detail"]


def test_upload_file_project_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("cma_projects", data=[])

    res = authed_client.post(
        f"/api/v1/projects/{uuid4()}/files",
        files={"file": ("test.xlsx", b"data", "application/octet-stream")},
    )
    assert res.status_code == 404


def test_upload_file_wrong_project_status(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    proj = make_project_row(project_id=proj_id, status="completed")
    mock_db.set_table("cma_projects", data=[proj])

    res = authed_client.post(
        f"/api/v1/projects/{proj_id}/files",
        files={"file": ("test.xlsx", b"data", "application/octet-stream")},
    )
    assert res.status_code == 409


def test_upload_file_no_auth(unauthed_client: TestClient):
    res = unauthed_client.post(
        f"/api/v1/projects/{uuid4()}/files",
        files={"file": ("test.xlsx", b"data", "application/octet-stream")},
    )
    assert res.status_code == 401


def test_list_uploaded_files(authed_client: TestClient, mock_db):
    proj_id = str(uuid4())
    files = [make_file_row(), make_file_row()]
    mock_db.set_table("uploaded_files", data=files)

    res = authed_client.get(f"/api/v1/projects/{proj_id}/files")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["items"]) == 2


def test_list_uploaded_files_empty(authed_client: TestClient, mock_db):
    mock_db.set_table("uploaded_files", data=[])

    res = authed_client.get(f"/api/v1/projects/{uuid4()}/files")
    assert res.status_code == 200
    assert res.json()["data"]["items"] == []


def test_download_file_success(authed_client: TestClient, mock_db):
    file_id = str(uuid4())
    mock_db.set_table("uploaded_files", data=[{
        "storage_path": "firm/proj/file.xlsx",
        "file_name": "file.xlsx",
    }])

    with patch("app.api.v1.endpoints.files.get_signed_url", return_value="https://signed.url/file"):
        res = authed_client.get(f"/api/v1/files/{file_id}/download")

    assert res.status_code == 200
    data = res.json()["data"]
    assert "download_url" in data
    assert data["file_name"] == "file.xlsx"
    assert data["expires_in"] == 3600


def test_download_file_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("uploaded_files", data=[])

    res = authed_client.get(f"/api/v1/files/{uuid4()}/download")
    assert res.status_code == 404


def test_list_generated_files(authed_client: TestClient, mock_db):
    mock_db.set_table("generated_files", data=[])

    res = authed_client.get(f"/api/v1/projects/{uuid4()}/generated")
    assert res.status_code == 200
    assert res.json()["data"]["items"] == []


def test_download_generated_file_not_found(authed_client: TestClient, mock_db):
    mock_db.set_table("generated_files", data=[])

    res = authed_client.get(f"/api/v1/generated/{uuid4()}/download")
    assert res.status_code == 404
