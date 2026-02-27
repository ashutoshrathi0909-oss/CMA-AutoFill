"""Tests for auth middleware and /me endpoint."""
from fastapi.testclient import TestClient
from tests.conftest import TEST_USER, TEST_FIRM_ID


def test_me_returns_user_info(authed_client: TestClient, mock_db):
    mock_db.set_table("firms", data=[{
        "id": str(TEST_FIRM_ID),
        "name": "Test Firm",
        "plan": "free",
    }])
    res = authed_client.get("/api/v1/me")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["email"] == TEST_USER.email
    assert data["full_name"] == TEST_USER.full_name
    assert data["role"] == TEST_USER.role
    assert data["firm"] is not None


def test_me_without_auth_returns_401(unauthed_client: TestClient):
    res = unauthed_client.get("/api/v1/me")
    assert res.status_code == 401


def test_me_response_follows_standard_format(authed_client: TestClient, mock_db):
    mock_db.set_table("firms", data=[{
        "id": str(TEST_FIRM_ID),
        "name": "Test Firm",
        "plan": "free",
    }])
    res = authed_client.get("/api/v1/me")
    body = res.json()
    assert "data" in body
    assert "error" in body
    assert body["error"] is None
