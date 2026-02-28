"""
Standalone extraction service callable from the pipeline orchestrator.

Extracted from the /extract API endpoint so the orchestrator can call it
without going through HTTP.
"""

import logging
from typing import Dict, Any, List

from pydantic import BaseModel

from app.db.supabase_client import get_supabase
from app.services.extraction.excel_parser import parse_excel
from app.services.extraction.pdf_parser import parse_pdf, is_digital_pdf
from app.services.extraction.vision_extractor import extract_with_vision
from app.services.extraction.merger import merge_and_save_data

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    files_processed: int
    files_succeeded: int
    files_failed: int
    total_line_items: int
    results: List[Dict[str, Any]]


def extract_project(project_id: str, firm_id: str) -> ExtractionResult:
    """
    Extract data from all pending uploaded files for a project.

    Downloads each file from storage, parses it based on type,
    stores extracted data on the file row, then merges all results.

    Raises ValueError if all files fail.
    """
    db = get_supabase()

    # Get files pending extraction (exclude soft-deleted and already extracted)
    files_resp = (
        db.table("uploaded_files")
        .select("*")
        .eq("cma_project_id", project_id)
        .eq("firm_id", firm_id)
        .neq("extraction_status", "deleted")
        .execute()
    )

    files = files_resp.data or []
    if not files:
        raise ValueError("No files found for extraction")

    files_succeeded = 0
    files_failed = 0
    total_items = 0
    results: List[Dict[str, Any]] = []

    for f in files:
        file_id = f["id"]
        file_name = f.get("file_name", "unknown")

        db.table("uploaded_files").update(
            {"extraction_status": "processing"}
        ).eq("id", file_id).execute()

        try:
            storage_path = f["storage_path"]
            file_bytes = db.storage.from_("cma-files").download(storage_path)

            ext = f.get("file_type", "")
            extracted_data = None

            if ext in ("xlsx", "xls"):
                extracted_data = parse_excel(file_bytes, file_name)
            elif ext == "csv":
                extracted_data = parse_excel(file_bytes, file_name, is_csv=True)
            elif ext == "pdf":
                if is_digital_pdf(file_bytes):
                    extracted_data = parse_pdf(file_bytes, file_name)
                else:
                    extracted_data = extract_with_vision(
                        file_bytes, file_name, "application/pdf",
                        firm_id, project_id,
                        f.get("document_type", "auto-detect"),
                    )
            elif ext in ("jpg", "png"):
                mime = "image/jpeg" if ext == "jpg" else "image/png"
                extracted_data = extract_with_vision(
                    file_bytes, file_name, mime,
                    firm_id, project_id,
                    f.get("document_type", "auto-detect"),
                )
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            items_count = len(extracted_data.get("line_items", []))
            db.table("uploaded_files").update({
                "extraction_status": "completed",
                "extracted_data": extracted_data,
            }).eq("id", file_id).execute()

            total_items += items_count
            files_succeeded += 1

            results.append({
                "file_id": file_id,
                "file_name": file_name,
                "status": "completed",
                "line_items_count": items_count,
                "document_type": extracted_data.get("document_type", "other"),
            })

        except Exception as e:
            logger.error("Extraction failed for file %s: %s", file_name, e)
            files_failed += 1
            db.table("uploaded_files").update({
                "extraction_status": "failed",
                "extracted_data": {"error": str(e)},
            }).eq("id", file_id).execute()

            results.append({
                "file_id": file_id,
                "file_name": file_name,
                "status": "failed",
                "error": str(e),
            })

    # Merge extracted data across files
    if files_succeeded > 0:
        try:
            merge_and_save_data(project_id, firm_id)
        except Exception as e:
            logger.error("Merge failed for project %s: %s", project_id, e)
            raise ValueError(f"Extraction succeeded but merge failed: {e}") from e
    else:
        raise ValueError("All files failed to extract")

    return ExtractionResult(
        files_processed=len(files),
        files_succeeded=files_succeeded,
        files_failed=files_failed,
        total_line_items=total_items,
        results=results,
    )
