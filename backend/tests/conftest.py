import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
from datetime import datetime

from app.models.user import CurrentUser


# ── Reusable test data ──────────────────────────────────────

TEST_FIRM_ID = uuid4()
TEST_USER_ID = uuid4()

TEST_USER = CurrentUser(
    id=TEST_USER_ID,
    firm_id=TEST_FIRM_ID,
    email="test@example.com",
    full_name="Test User",
    role="owner",
)

OTHER_FIRM_ID = uuid4()
OTHER_USER = CurrentUser(
    id=uuid4(),
    firm_id=OTHER_FIRM_ID,
    email="other@example.com",
    full_name="Other User",
    role="owner",
)

NOW_ISO = datetime.now().isoformat() + "Z"


def make_client_row(
    client_id: str | None = None,
    firm_id: UUID | None = None,
    name: str = "Test Corp",
    entity_type: str = "trading",
) -> dict:
    return {
        "id": client_id or str(uuid4()),
        "firm_id": str(firm_id or TEST_FIRM_ID),
        "name": name,
        "entity_type": entity_type,
        "pan_number": None,
        "gst_number": None,
        "contact_person": None,
        "contact_email": None,
        "contact_phone": None,
        "address": None,
        "is_active": True,
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
    }


def make_project_row(
    project_id: str | None = None,
    client_id: str | None = None,
    firm_id: UUID | None = None,
    status: str = "draft",
) -> dict:
    return {
        "id": project_id or str(uuid4()),
        "firm_id": str(firm_id or TEST_FIRM_ID),
        "client_id": client_id or str(uuid4()),
        "financial_year": "2024-25",
        "bank_name": None,
        "loan_type": None,
        "loan_amount": None,
        "status": status,
        "extracted_data": None,
        "classification_results": None,
        "validation_errors": None,
        "pipeline_progress": 0,
        "pipeline_current_step": None,
        "error_message": None,
        "created_by": str(TEST_USER_ID),
        "created_at": NOW_ISO,
        "updated_at": NOW_ISO,
    }


def make_file_row(file_id: str | None = None) -> dict:
    return {
        "id": file_id or str(uuid4()),
        "firm_id": str(TEST_FIRM_ID),
        "cma_project_id": str(uuid4()),
        "file_name": "test.xlsx",
        "file_type": "xlsx",
        "file_size": 1024,
        "storage_path": f"{TEST_FIRM_ID}/proj/20260226_test.xlsx",
        "document_type": "balance_sheet",
        "extraction_status": "pending",
        "uploaded_by": str(TEST_USER_ID),
        "created_at": NOW_ISO,
    }


# ── Mock helpers ────────────────────────────────────────────

class MockQueryBuilder:
    """Chainable mock that simulates Supabase query builder."""

    def __init__(self, data: list | None = None, count: int | None = None):
        self._data = data if data is not None else []
        self._count = count

    def select(self, *args, **kwargs):
        return self

    def insert(self, *args, **kwargs):
        return self

    def update(self, *args, **kwargs):
        return self

    def delete(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def neq(self, *args, **kwargs):
        return self

    def ilike(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def gte(self, *args, **kwargs):
        return self

    def lte(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def range(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        result = MagicMock()
        result.data = self._data
        result.count = self._count
        return result


class MockSupabase:
    """Mock Supabase client that routes table() calls to MockQueryBuilders."""

    def __init__(self):
        self._tables: dict[str, MockQueryBuilder] = {}
        self.storage = MagicMock()

    def set_table(self, name: str, data: list | None = None, count: int | None = None):
        self._tables[name] = MockQueryBuilder(data=data, count=count)

    def table(self, name: str):
        if name in self._tables:
            return self._tables[name]
        return MockQueryBuilder()


# ── Fixtures ────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Provide a MockSupabase and patch get_supabase to return it."""
    db = MockSupabase()
    patches = [
        "app.db.supabase_client.get_supabase",
        "app.core.auth.get_supabase",
        "app.api.v1.endpoints.clients.get_supabase",
        "app.api.v1.endpoints.projects.get_supabase",
        "app.api.v1.endpoints.files.get_supabase",
        "app.api.v1.endpoints.dashboard.get_supabase",
        "app.api.v1.endpoints.auth.get_supabase",
        "app.api.v1.endpoints.extraction.get_supabase",
        "app.services.extraction.merger.get_supabase",
        "app.services.gemini_client.get_supabase",
    ]
    # Stack all patches
    import contextlib
    with contextlib.ExitStack() as stack:
        for target in patches:
            stack.enter_context(patch(target, return_value=db))
        yield db


@pytest.fixture
def authed_client(mock_db):
    """FastAPI TestClient with mocked auth that returns TEST_USER."""
    from main import app
    from app.core.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def unauthed_client(mock_db):
    """FastAPI TestClient with NO auth override — requests get 401."""
    from main import app

    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
