from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
import uuid

router = APIRouter()

class ExtractRequest(BaseModel):
    file_ids: Optional[List[str]] = None
    force_reextract: bool = False

@router.post("/{project_id}/extract", response_model=StandardResponse[dict])
def extract_project_files(project_id: str, payload: ExtractRequest = None, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    # 1. Validate project
    proj_resp = db.table("cma_projects").select("id, status").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project = proj_resp.data[0]
    
    # 2. Get files
    query = db.table("uploaded_files").select("*").eq("cma_project_id", project_id).eq("firm_id", str(current_user.firm_id))
    
    if payload and payload.file_ids:
        query = query.in_("id", payload.file_ids)
    elif not payload or not payload.force_reextract:
        query = query.eq("extraction_status", "pending")
        
    files_resp = query.execute()
    if not files_resp.data:
        raise HTTPException(status_code=400, detail="No files pending extraction")
        
    files = files_resp.data
    
    # 3. Update status to extracting
    db.table("cma_projects").update({
        "status": "extracting",
        "pipeline_progress": 10
    }).eq("id", project_id).execute()
    
    files_succeeded = 0
    files_failed = 0
    total_items = 0
    results = []
    
    for f in files:
        file_id = f["id"]
        db.table("uploaded_files").update({"extraction_status": "processing"}).eq("id", file_id).execute()
        
        try:
            # Download file bytes
            storage_path = f["storage_path"]
            storage_res = db.storage.from_("cma-files").download(storage_path)
            # storage_res is bytes in supabase-py currently
            file_bytes = storage_res
            file_name = f["file_name"]
            
            ext = f["file_type"]
            extracted_data = None
            
            if ext in ["xlsx", "xls", "csv"]:
                extracted_data = parse_excel(file_bytes, file_name)
            elif ext == "pdf":
                if is_digital_pdf(file_bytes):
                    extracted_data = parse_pdf(file_bytes, file_name)
                else:
                    extracted_data = extract_with_vision(file_bytes, file_name, "application/pdf", str(current_user.firm_id), project_id, f.get("document_type", "auto-detect"))
            elif ext in ["jpg", "png"]:
                mime = "image/jpeg" if ext == "jpg" else "image/png"
                extracted_data = extract_with_vision(file_bytes, file_name, mime, str(current_user.firm_id), project_id, f.get("document_type", "auto-detect"))
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
            db.table("uploaded_files").update({
                "extraction_status": "completed",
                "extracted_data": extracted_data
            }).eq("id", file_id).execute()
            
            items_count = len(extracted_data.get("line_items", []))
            total_items += items_count
            files_succeeded += 1
            
            results.append({
                "file_id": file_id,
                "file_name": file_name,
                "status": "completed",
                "line_items_count": items_count,
                "document_type": extracted_data.get("document_type", "other")
            })
            
        except Exception as e:
            files_failed += 1
            db.table("uploaded_files").update({
                "extraction_status": "failed",
                "extracted_data": {"error": str(e)}
            }).eq("id", file_id).execute()
            
            results.append({
                "file_id": file_id,
                "file_name": file_name,
                "status": "failed",
                "error": str(e)
            })
            
    # Complete
    
    if files_succeeded > 0:
        # Task 4.7: merge logic
        merge_and_save_data(project_id, str(current_user.firm_id))
    else:
        # all failed
        db.table("cma_projects").update({
            "status": "error",
            "error_message": "All files failed to extract."
        }).eq("id", project_id).execute()
        
    return StandardResponse(data={
        "project_id": project_id,
        "files_processed": len(files),
        "files_succeeded": files_succeeded,
        "files_failed": files_failed,
        "total_line_items_extracted": total_items,
        "results": results
    })
