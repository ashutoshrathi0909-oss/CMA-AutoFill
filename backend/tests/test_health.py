"""Tests for health check endpoints (root level, no auth required)."""
from fastapi.testclient import TestClient


def test_root_returns_message(authed_client: TestClient):
    res = authed_client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "CMA AutoFill API v1"


def test_health_returns_status_version_uptime(authed_client: TestClient):
    res = authed_client.get("/health")
    data = res.json()
    assert res.status_code == 200
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "database" in data


def test_health_db(authed_client: TestClient):
    res = authed_client.get("/health/db")
    assert res.status_code == 200
    data = res.json()
    # With mocked supabase, get_supabase() won't raise, so status should be connected
    assert data["status"] == "connected"


def test_health_no_auth_required(unauthed_client: TestClient):
    """Health endpoints should work even without an auth token."""
    res = unauthed_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
