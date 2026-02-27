"""Tests for dashboard stats endpoint."""
from fastapi.testclient import TestClient
from tests.conftest import TEST_FIRM_ID


def test_dashboard_stats_success(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)
    mock_db.set_table("llm_usage_log", data=[])

    res = authed_client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()["data"]

    # All expected top-level keys
    assert "total_clients" in data
    assert "active_clients" in data
    assert "total_projects" in data
    assert "projects_by_status" in data
    assert "pending_reviews" in data
    assert "this_month" in data
    assert "llm_usage" in data
    assert "recent_projects" in data


def test_dashboard_stats_all_statuses_present(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)
    mock_db.set_table("llm_usage_log", data=[])

    res = authed_client.get("/api/v1/dashboard/stats")
    statuses = res.json()["data"]["projects_by_status"]
    expected = ["draft", "extracting", "classifying", "reviewing", "validating", "generating", "completed", "error"]
    for s in expected:
        assert s in statuses


def test_dashboard_stats_this_month_structure(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)
    mock_db.set_table("llm_usage_log", data=[])

    res = authed_client.get("/api/v1/dashboard/stats")
    this_month = res.json()["data"]["this_month"]
    assert "projects_created" in this_month
    assert "projects_completed" in this_month


def test_dashboard_stats_llm_usage_structure(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)
    mock_db.set_table("llm_usage_log", data=[])

    res = authed_client.get("/api/v1/dashboard/stats")
    llm = res.json()["data"]["llm_usage"]
    assert "total_cost_usd" in llm
    assert "total_tokens" in llm
    assert "this_month_cost_usd" in llm


def test_dashboard_stats_no_auth(unauthed_client: TestClient):
    res = unauthed_client.get("/api/v1/dashboard/stats")
    assert res.status_code == 401


def test_dashboard_stats_follows_standard_format(authed_client: TestClient, mock_db):
    mock_db.set_table("clients", data=[], count=0)
    mock_db.set_table("cma_projects", data=[], count=0)
    mock_db.set_table("review_queue", data=[], count=0)
    mock_db.set_table("llm_usage_log", data=[])

    res = authed_client.get("/api/v1/dashboard/stats")
    body = res.json()
    assert "data" in body
    assert "error" in body
    assert body["error"] is None
