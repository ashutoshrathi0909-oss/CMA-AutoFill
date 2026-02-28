from typing import Dict, Any, List, Optional
from uuid import UUID
import os
import tempfile
import time
from pydantic import BaseModel
from app.services.validation.validator import validate_project, ValidationResult
from app.services.excel.data_transformer import transform_for_writer
from app.services.excel.cma_writer import CMAWriter
from app.db.supabase_client import get_supabase
import logging
import uuid
from datetime import datetime

class GenerationResult(BaseModel):
    success: bool
    project_id: str
    generated_file_id: Optional[str] = None
    file_name: str
    file_size: int
    storage_path: str
    validation: Optional[ValidationResult]
    warnings: List[str]
    generation_time_ms: int
    version: int

def generate_cma(project_id: str, firm_id: str, skip_validation: bool = False) -> GenerationResult:
    start_time = time.time()
    db = get_supabase()
    
    # 1. Load classification data
    proj_resp = db.table("cma_projects").select("id, client_id, classification_data").eq("id", project_id).eq("firm_id", firm_id).execute()
    if not proj_resp.data:
        raise ValueError("Project not found")
        
    project = proj_resp.data[0]
    client_id = project["client_id"]
    client_resp = db.table("clients").select("name, entity_type").eq("id", client_id).execute()
    
    client_name = client_resp.data[0]["name"] if client_resp.data else "Unknown"
    entity_type = client_resp.data[0]["entity_type"] if client_resp.data else "trading"
    client_name_safe = client_name.replace(" ", "")
    
    classification_data = project.get("classification_data", {})
    if not classification_data:
        raise ValueError("No classification data found on project")
        
    validation_res = None
    warnings = []
    
    # 2. Run validations
    if not skip_validation:
        validation_res = validate_project(project_id, classification_data, entity_type)
        if not validation_res.can_generate:
            return GenerationResult(
                success=False,
                project_id=project_id,
                file_name="",
                file_size=0,
                storage_path="",
                validation=validation_res,
                warnings=warnings,
                generation_time_ms=int((time.time() - start_time) * 1000),
                version=0
            )
        else:
            warnings = [chk.message for chk in validation_res.checks if not chk.passed]
            
    # 3. Transform data
    items_list = classification_data.get("items", [])
    transformed_data = transform_for_writer(items_list, entity_type)
    
    # 4. Copy template and Generate CMA Excel
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "reference", "CMA.xlsm")
    # For CI and edge cases it might not exist since it's a mock template. If it doesn't we'll just fail cleanly.
    
    fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    
    try:
        writer = CMAWriter(template_path)
        writer.write(transformed_data, tmp_path)
        
        # 5. Get file size
        file_size = os.path.getsize(tmp_path)
        
        # 6. Calc version logic
        gen_files = db.table("generated_files").select("version").eq("cma_project_id", project_id).execute()
        current_version = max([gf["version"] for gf in gen_files.data], default=0) + 1
        
        file_name = f"CMA_{client_name_safe}_2024-25_v{current_version}.xlsx"
        storage_path = f"{firm_id}/{project_id}/generated/{file_name}"
        
        # Read bits and upload to Supabase Bucket
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()
            
        db.storage.from_("cma-files").upload(storage_path, file_bytes, {"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
        
        # 7. DB Inserts
        gen_id = str(uuid.uuid4())
        db.table("generated_files").insert({
            "id": gen_id,
            "firm_id": firm_id,
            "cma_project_id": project_id,
            "file_name": file_name,
            "storage_path": storage_path,
            "version": current_version,
            "file_size_bytes": file_size
        }).execute()
        
        db.table("cma_projects").update({
            "status": "completed",
            "pipeline_progress": 100
        }).eq("id", project_id).execute()
        
        gen_time = int((time.time() - start_time) * 1000)
        
        return GenerationResult(
            success=True,
            project_id=project_id,
            generated_file_id=gen_id,
            file_name=file_name,
            file_size=file_size,
            storage_path=storage_path,
            validation=validation_res,
            warnings=warnings,
            generation_time_ms=gen_time,
            version=current_version
        )
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
