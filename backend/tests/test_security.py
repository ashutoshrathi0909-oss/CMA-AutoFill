"""Tests for security hardening (Phase 11 — Task 11.2)."""

import pytest
from app.core.security import sanitize_filename, validate_uuid, validate_pagination
from fastapi import HTTPException


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("report.xlsx") == "report.xlsx"

    def test_spaces_replaced(self):
        assert sanitize_filename("my report 2024.xlsx") == "my_report_2024.xlsx"

    def test_path_traversal_unix(self):
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        assert "passwd" in result

    def test_path_traversal_windows(self):
        result = sanitize_filename("..\\..\\windows\\system32\\config")
        assert ".." not in result
        assert "\\" not in result

    def test_null_bytes_removed(self):
        result = sanitize_filename("file\x00.xlsx")
        assert "\x00" not in result
        assert result == "file.xlsx"

    def test_empty_filename(self):
        result = sanitize_filename("")
        assert len(result) > 0

    def test_dot_only_filename(self):
        result = sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_long_filename_truncated(self):
        long_name = "a" * 300 + ".xlsx"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_special_characters_removed(self):
        result = sanitize_filename("file<>|:*?.xlsx")
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert ":" not in result
        assert "?" not in result
        assert "*" not in result


class TestValidateUuid:
    def test_valid_uuid(self):
        valid = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_uuid(valid) == valid

    def test_invalid_uuid(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_uuid("not-a-uuid")
        assert exc_info.value.status_code == 422

    def test_empty_string(self):
        with pytest.raises(HTTPException):
            validate_uuid("")

    def test_custom_param_name(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_uuid("bad", param_name="project_id")
        assert "project_id" in exc_info.value.detail


class TestValidatePagination:
    def test_normal_values(self):
        assert validate_pagination(1, 20) == (1, 20)

    def test_zero_page_clamped(self):
        page, _ = validate_pagination(0, 20)
        assert page >= 1

    def test_negative_page_clamped(self):
        page, _ = validate_pagination(-5, 20)
        assert page >= 1

    def test_per_page_over_100_clamped(self):
        _, per_page = validate_pagination(1, 500)
        assert per_page == 100

    def test_per_page_zero_clamped(self):
        _, per_page = validate_pagination(1, 0)
        assert per_page >= 1
