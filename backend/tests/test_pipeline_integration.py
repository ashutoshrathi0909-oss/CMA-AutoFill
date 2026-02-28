"""
Task 8.7: Pipeline integration tests.

Tests run with fully mocked DB + services so no external dependencies needed.
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock, patch
from app.services.pipeline.orchestrator import (
    run_pipeline,
    resume_pipeline,
    should_run,
    PipelineOptions,
    PipelineResult,
)
from app.services.pipeline.error_handler import with_retry, TransientError, PermanentError


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────
MOCK_PROJECT_ID = str(uuid4())
MOCK_FIRM_ID = str(uuid4())
MOCK_CLIENT_ID = str(uuid4())


def _make_mock_db():
    """Return a mock Supabase client with sensible defaults."""

    class MockResult:
        def __init__(self, data=None, count=0):
            self.data = data or []
            self.count = count

    class MockQuery:
        def __init__(self, data=None, count=0):
            self._data = data or []
            self._count = count

        def select(self, *a, **kw):
            return self
        def eq(self, *a, **kw):
            return self
        def neq(self, *a, **kw):
            return self
        def gte(self, *a, **kw):
            return self
        def in_(self, *a, **kw):
            return self
        def ilike(self, *a, **kw):
            return self
        def or_(self, *a, **kw):
            return self
        def order(self, *a, **kw):
            return self
        def range(self, *a, **kw):
            return self
        def update(self, *a, **kw):
            return self
        def insert(self, *a, **kw):
            return self
        def delete(self, *a, **kw):
            return self

        def execute(self):
            return MockResult(self._data, self._count)

    class MockStorage:
        class Bucket:
            def upload(self, *a, **kw): ...
            def create_signed_url(self, *a, **kw):
                return {"signedURL": "http://mock.url"}
        def from_(self, _):
            return self.Bucket()

    class DB:
        storage = MockStorage()

        def table(self, name):
            if name == "cma_projects":
                return MockQuery([{
                    "id": MOCK_PROJECT_ID,
                    "status": "draft",
                    "client_id": MOCK_CLIENT_ID,
                    "is_processing": False,
                    "pipeline_steps": {},
                    "classification_data": {
                        "items": [
                            {"item_name": "Sales", "target_row": 5, "target_sheet": "operating_statement", "item_amount": 1500000}
                        ]
                    },
                    "error_message": None,
                    "financial_year": "2024-25",
                }])
            if name == "clients":
                return MockQuery([{"name": "Mehta Computers", "entity_type": "trading"}])
            if name == "uploaded_files":
                return MockQuery([{"id": "f1"}], count=1)
            if name == "review_queue":
                return MockQuery([], count=0)
            if name == "generated_files":
                return MockQuery([])
            if name == "classification_precedents":
                return MockQuery([])
            return MockQuery([])

    return DB()


# ─────────────────────────────────────────────────────────────────────────
# Test: should_run helper
# ─────────────────────────────────────────────────────────────────────────
class TestShouldRun:
    def test_force_reprocess_runs_everything(self):
        opts = PipelineOptions(force_reprocess=True)
        assert should_run("extract", "completed", opts) is True
        assert should_run("generate", "completed", opts) is True

    def test_start_from_skips_earlier_steps(self):
        opts = PipelineOptions(start_from="validate")
        assert should_run("extract", "draft", opts) is False
        assert should_run("classify", "draft", opts) is False
        assert should_run("validate", "draft", opts) is True
        assert should_run("generate", "draft", opts) is True

    def test_default_flow_from_draft(self):
        opts = PipelineOptions()
        assert should_run("extract", "draft", opts) is True
        assert should_run("classify", "draft", opts) is True


# ─────────────────────────────────────────────────────────────────────────
# Test: Happy path (skip_review=True → full completion)
# ─────────────────────────────────────────────────────────────────────────
class TestHappyPath:
    def test_full_pipeline_skip_review(self, monkeypatch):
        mock_db = _make_mock_db()
        monkeypatch.setattr("app.services.pipeline.orchestrator.get_supabase", lambda: mock_db)

        # Mock extraction
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_extract",
            lambda pid, fid: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, duration_ms=100),
        )
        # Mock classification
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_classify",
            lambda pid, fid, et: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, duration_ms=200, llm_cost_usd=0.002),
        )
        # Mock review check (no items)
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_review_check",
            lambda pid, fid, opts: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, needs_review=False, duration_ms=10),
        )
        # Mock validation
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_validate",
            lambda pid, fid, et, skip=False: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, duration_ms=15),
        )
        # Mock generation
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_generate",
            lambda pid, fid, skip_validation=False: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, duration_ms=50),
        )

        result = run_pipeline(MOCK_PROJECT_ID, MOCK_FIRM_ID, PipelineOptions(skip_review=True))

        assert result.stopped_reason == "completed"
        assert "extract" in result.completed_steps
        assert "generate" in result.completed_steps
        assert result.duration_ms >= 0


# ─────────────────────────────────────────────────────────────────────────
# Test: Pipeline pauses for review
# ─────────────────────────────────────────────────────────────────────────
class TestReviewPause:
    def test_pipeline_pauses_at_review(self, monkeypatch):
        mock_db = _make_mock_db()
        monkeypatch.setattr("app.services.pipeline.orchestrator.get_supabase", lambda: mock_db)

        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_extract",
            lambda pid, fid: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, duration_ms=100),
        )
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_classify",
            lambda pid, fid, et: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, needs_review=True, review_count=5, duration_ms=200, llm_cost_usd=0.003),
        )
        # Review check finds items
        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_review_check",
            lambda pid, fid, opts: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=True, needs_review=True, review_count=5, duration_ms=10),
        )

        result = run_pipeline(MOCK_PROJECT_ID, MOCK_FIRM_ID, PipelineOptions())

        assert result.stopped_reason == "awaiting_review"
        assert "extract" in result.completed_steps
        assert "classify" in result.completed_steps
        assert "generate" not in result.completed_steps


# ─────────────────────────────────────────────────────────────────────────
# Test: Extraction failure
# ─────────────────────────────────────────────────────────────────────────
class TestExtractionFailure:
    def test_extract_fails_stops_pipeline(self, monkeypatch):
        mock_db = _make_mock_db()
        monkeypatch.setattr("app.services.pipeline.orchestrator.get_supabase", lambda: mock_db)

        monkeypatch.setattr(
            "app.services.pipeline.orchestrator._run_extract",
            lambda pid, fid: __import__("app.services.pipeline.orchestrator", fromlist=["StepResult"]).StepResult(success=False, error="Invalid PDF", duration_ms=50),
        )

        result = run_pipeline(MOCK_PROJECT_ID, MOCK_FIRM_ID)

        assert result.stopped_reason == "extraction_failed"
        assert len(result.errors) == 1
        assert result.errors[0]["step"] == "extract"


# ─────────────────────────────────────────────────────────────────────────
# Test: Retry logic (error_handler)
# ─────────────────────────────────────────────────────────────────────────
class TestRetryLogic:
    def test_transient_retries_succeed(self):
        call_count = 0

        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransientError("rate limited")
            return "ok"

        result = with_retry(flaky, max_retries=3, base_delay=0.01)
        assert result == "ok"
        assert call_count == 3

    def test_permanent_error_no_retry(self):
        with pytest.raises(PermanentError):
            with_retry(lambda: (_ for _ in ()).throw(PermanentError("bad data")), max_retries=3, base_delay=0.01)
