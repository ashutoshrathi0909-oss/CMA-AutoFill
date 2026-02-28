from fastapi import APIRouter, Depends, Query, HTTPException, Request, UploadFile, File, Form
from typing import Optional
from app.core.auth import get_current_user
from app.core.security import limiter, sanitize_filename
from app.models.user import CurrentUser
from app.models.file import FileResponse, FileListResponse, GeneratedFileResponse, GeneratedFileListResponse
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from app.services.storage import upload_file, get_signed_url

router = APIRouter()

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf', 'jpg', 'png', 'csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/projects/{project_id}/files", response_model=StandardResponse[FileResponse], status_code=201)
@limiter.limit("20/hour")
async def upload_project_file(
    request: Request,
    project_id: str,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    db = get_supabase()
    
    # Validate project
    proj_resp = db.table("cma_projects").select("id, status").eq("id", project_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project = proj_resp.data[0]
    if project["status"] not in ["draft", "extracting", "error"]:
        raise HTTPException(status_code=409, detail=f"Cannot upload files to project in '{project['status']}' status")

    # Sanitize filename to prevent path traversal
    safe_name = sanitize_filename(file.filename or "upload")

    # Validate file extension
    ext = safe_name.split(".")[-1].lower() if "." in safe_name else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"File type '.{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
    # Read file bytes and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        
    # Upload to storage using the storage service
    try:
        storage_path = upload_file(
            firm_id=str(current_user.firm_id),
            project_id=project_id,
            file_name=safe_name,
            file_bytes=file_bytes,
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to storage: {str(e)}")

    # Insert metadata
    file_record = {
        "firm_id": str(current_user.firm_id),
        "cma_project_id": project_id,
        "file_name": safe_name,
        "file_type": ext,
        "file_size": len(file_bytes),
        "storage_path": storage_path,
        "document_type": document_type,
        "extraction_status": "pending",
        "uploaded_by": str(current_user.id)
    }
    
    res = db.table("uploaded_files").insert(file_record).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save file metadata")
        
    inserted_file = res.data[0]
    
    # Audit logic
    db.table("audit_log").insert({
        "firm_id": str(current_user.firm_id),
        "user_id": str(current_user.id),
        "action": "upload_file",
        "entity_type": "uploaded_file",
        "entity_id": inserted_file["id"],
        "metadata": {"file_name": safe_name, "project_id": project_id}
    }).execute()
    
    return StandardResponse(data=FileResponse(**inserted_file))

@router.get("/projects/{project_id}/files", response_model=StandardResponse[FileListResponse])
def list_uploaded_files(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    # Check project ownership implicitly by enforcing firm_id on the files
    res = db.table("uploaded_files").select("*").eq("cma_project_id", project_id).eq("firm_id", str(current_user.firm_id)).order("created_at", desc=True).execute()
    
    # We don't 404 if project is found but empty, but should we 404 if project doesn't exist?
    # Task 3.6 says: 'List files for empty project → returns empty array, not error'
    files = res.data
    return StandardResponse(data=FileListResponse(items=[FileResponse(**f) for f in files]))

@router.get("/files/{file_id}/download", response_model=StandardResponse[dict])
def download_uploaded_file(file_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    # Auth constraint check
    res = db.table("uploaded_files").select("storage_path, file_name").eq("id", file_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_record = res.data[0]
    
    try:
        url = get_signed_url(file_record["storage_path"], 3600)
        # handle supabase structure
        if isinstance(url, dict) and 'signedURL' in url:
            url = url['signedURL']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download url: {str(e)}")
        
    return StandardResponse(data={
        "download_url": url,
        "file_name": file_record["file_name"],
        "expires_in": 3600
    })

@router.get("/projects/{project_id}/generated", response_model=StandardResponse[GeneratedFileListResponse])
def list_generated_files(project_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    res = db.table("generated_files").select("*").eq("cma_project_id", project_id).eq("firm_id", str(current_user.firm_id)).order("generated_at", desc=True).execute()
    files = res.data
    return StandardResponse(data=GeneratedFileListResponse(items=[GeneratedFileResponse(**f) for f in files]))

@router.get("/generated/{file_id}/download", response_model=StandardResponse[dict])
def download_generated_file(file_id: str, current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    res = db.table("generated_files").select("storage_path, file_name").eq("id", file_id).eq("firm_id", str(current_user.firm_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Generated file not found")
        
    file_record = res.data[0]
    
    try:
        url = get_signed_url(file_record["storage_path"], 3600)
        if isinstance(url, dict) and 'signedURL' in url:
            url = url['signedURL']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate download url: {str(e)}")
        
    return StandardResponse(data={
        "download_url": url,
        "file_name": file_record["file_name"],
        "expires_in": 3600
    })
