import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from app.services.extraction.excel_parser import parse_excel
from app.services.extraction.pdf_parser import parse_pdf, is_digital_pdf
from app.services.extraction.vision_extractor import extract_with_vision
from app.services.extraction.merger import merge_and_save_data

logger = logging.getLogger(__name__)

router = APIRouter()


class ExtractRequest(BaseModel):
    file_ids: Optional[List[str]] = None
    force_reextract: bool = False


@router.post("/{project_id}/extract", response_model=StandardResponse[dict])
async def extract_project_files(
    project_id: str,
    payload: Optional[ExtractRequest] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    # 1. Validate project exists and is not soft-deleted
    proj_resp = (
        db.table("cma_projects")
        .select("id, status")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .neq("status", "error")
        .execute()
    )
    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Get files (exclude soft-deleted / already-extracted unless forced)
    query = (
        db.table("uploaded_files")
        .select("*")
        .eq("cma_project_id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .neq("extraction_status", "deleted")
    )

    if payload and payload.file_ids:
        query = query.in_("id", payload.file_ids)
    elif not payload or not payload.force_reextract:
        query = query.eq("extraction_status", "pending")

    files_resp = query.execute()
    if not files_resp.data:
        return StandardResponse(data={
            "project_id": project_id,
            "files_processed": 0,
            "files_succeeded": 0,
            "files_failed": 0,
            "total_line_items_extracted": 0,
            "results": [],
            "message": "No files pending extraction",
        })

    files = files_resp.data

    # 3. Update status to extracting
    db.table("cma_projects").update({
        "status": "extracting",
        "pipeline_progress": 10,
    }).eq("id", project_id).execute()

    # Audit log: extraction triggered
    try:
        db.table("audit_log").insert({
            "firm_id": str(current_user.firm_id),
            "action": "trigger_extraction",
            "entity_type": "cma_project",
            "entity_id": project_id,
            "metadata": {"file_count": len(files), "user_id": str(current_user.id)},
        }).execute()
    except Exception:
        logger.warning("Failed to write audit log for extraction trigger")

    files_succeeded = 0
    files_failed = 0
    total_items = 0
    results: List[dict] = []

    for f in files:
        file_id = f["id"]
        file_name = f.get("file_name", "unknown")

        db.table("uploaded_files").update({"extraction_status": "processing"}).eq("id", file_id).execute()

        try:
            storage_path = f["storage_path"]
            storage_res = db.storage.from_("cma-files").download(storage_path)
            file_bytes = storage_res

            ext = f["file_type"]
            extracted_data = None

            if ext in ["xlsx", "xls"]:
                extracted_data = parse_excel(file_bytes, file_name)
            elif ext == "csv":
                extracted_data = parse_excel(file_bytes, file_name, is_csv=True)
            elif ext == "pdf":
                if is_digital_pdf(file_bytes):
                    extracted_data = parse_pdf(file_bytes, file_name)
                else:
                    extracted_data = extract_with_vision(
                        file_bytes, file_name, "application/pdf",
                        str(current_user.firm_id), project_id,
                        f.get("document_type", "auto-detect"),
                    )
            elif ext in ["jpg", "png"]:
                mime = "image/jpeg" if ext == "jpg" else "image/png"
                extracted_data = extract_with_vision(
                    file_bytes, file_name, mime,
                    str(current_user.firm_id), project_id,
                    f.get("document_type", "auto-detect"),
                )
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            # Store lightweight metadata on file row, not the full payload
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

    # 4. Merge or mark error
    if files_succeeded > 0:
        try:
            merge_and_save_data(project_id, str(current_user.firm_id))
        except Exception as e:
            logger.error("Merge failed for project %s: %s", project_id, e)
            db.table("cma_projects").update({
                "status": "error",
                "error_message": f"Extraction succeeded but merge failed: {e}",
            }).eq("id", project_id).execute()
    else:
        db.table("cma_projects").update({
            "status": "error",
            "error_message": "All files failed to extract.",
        }).eq("id", project_id).execute()

    return StandardResponse(data={
        "project_id": project_id,
        "files_processed": len(files),
        "files_succeeded": files_succeeded,
        "files_failed": files_failed,
        "total_line_items_extracted": total_items,
        "results": results,
    })
