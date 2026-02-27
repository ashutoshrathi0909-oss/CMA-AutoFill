"""Tests for storage service functions."""
from unittest.mock import patch, MagicMock


def test_upload_file_returns_path():
    mock_db = MagicMock()
    with patch("app.services.storage.get_supabase", return_value=mock_db):
        from app.services.storage import upload_file

        path = upload_file(
            firm_id="firm-123",
            project_id="proj-456",
            file_name="test file.xlsx",
            file_bytes=b"content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    assert "firm-123" in path
    assert "proj-456" in path
    assert "test_file.xlsx" in path  # spaces replaced with underscores
    assert " " not in path
    mock_db.storage.from_("cma-files").upload.assert_called_once()


def test_get_signed_url_dict_response():
    mock_db = MagicMock()
    mock_db.storage.from_("cma-files").create_signed_url.return_value = {
        "signedURL": "https://example.com/signed"
    }
    with patch("app.services.storage.get_supabase", return_value=mock_db):
        from app.services.storage import get_signed_url

        url = get_signed_url("firm/proj/file.xlsx", 3600)

    assert url == "https://example.com/signed"


def test_get_signed_url_object_response():
    mock_db = MagicMock()
    mock_response = MagicMock()
    mock_response.signedURL = "https://example.com/signed-obj"
    # Make it not a dict so the first branch is skipped
    mock_db.storage.from_("cma-files").create_signed_url.return_value = mock_response
    with patch("app.services.storage.get_supabase", return_value=mock_db):
        from app.services.storage import get_signed_url

        url = get_signed_url("firm/proj/file.xlsx")

    assert url == "https://example.com/signed-obj"


def test_delete_file_calls_remove():
    mock_db = MagicMock()
    with patch("app.services.storage.get_supabase", return_value=mock_db):
        from app.services.storage import delete_file

        delete_file("firm/proj/file.xlsx")

    mock_db.storage.from_("cma-files").remove.assert_called_once_with(["firm/proj/file.xlsx"])
