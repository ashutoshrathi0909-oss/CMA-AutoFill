import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase
from app.services.validation.validator import validate_project
from app.services.excel.generator import generate_cma

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    skip_validation: bool = False


@router.post("/{project_id}/validate", response_model=StandardResponse[dict])
async def validate_cma_project(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    db = get_supabase()

    proj_resp = (
        db.table("cma_projects")
        .select("id, client_id, classification_data, status")
        .eq("id", project_id)
        .eq("firm_id", str(current_user.firm_id))
        .neq("status", "error")
        .execute()
    )

    if not proj_resp.data:
        raise HTTPException(status_code=404, detail="Project not found")

    project = proj_resp.data[0]

    if project["status"] not in ["reviewing", "validated", "completed"]:
        raise HTTPException(
            status_code=409,
            detail="Project must be reviewed or validated before validation check.",
        )

    client_resp = db.table("clients").select("entity_type").eq("id", project["client_id"]).execute()
    entity_type = client_resp.data[0]["entity_type"] if client_resp.data else "trading"
    classification_data = project.get("classification_data", {})

    val_res = validate_project(project_id, classification_data, entity_type)

    # Audit log
    try:
        db.table("audit_log").insert({
            "firm_id": str(current_user.firm_id),
            "action": "validate_project",
            "entity_type": "cma_project",
            "entity_id": project_id,
            "metadata": {
                "passed": val_res.passed,
                "errors": val_res.errors,
                "warnings": val_res.warnings,
            },
        }).execute()
    except Exception:
        logger.warning("Failed to write audit log for validation")

    return StandardResponse(data={
        "passed": val_res.passed,
        "total_checks": val_res.total_checks,
        "errors": val_res.errors,
        "warnings": val_res.warnings,
        "can_generate": val_res.can_generate,
        "checks": [c.model_dump() for c in val_res.checks],
        "summary": val_res.summary,
    })


@router.post("/{project_id}/generate", response_model=StandardResponse[dict])
async def generate_cma_file(
    project_id: str,
    req: Optional[GenerateRequest] = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    skip_val = req.skip_validation if req else False

    db = get_supabase()

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

    project = proj_resp.data[0]

    if project["status"] in ["draft", "extracting", "extracted", "classifying"]:
        raise HTTPException(status_code=409, detail="Cannot generate Excel before classification passes")

    try:
        gen_res = generate_cma(project_id, str(current_user.firm_id), skip_val)
    except Exception as e:
        logger.error("Generation failed for project %s: %s", project_id, e)
        raise HTTPException(status_code=500, detail="Generation failed. Please try again.")

    if not gen_res.success:
        raise HTTPException(status_code=422, detail={
            "message": "Validation failed — fix errors before generating",
            "validation": gen_res.validation.model_dump() if gen_res.validation else None,
            "warnings": gen_res.warnings,
        })

    # Get download URL
    download_url = ""
    try:
        url_res = db.storage.from_("cma-files").create_signed_url(gen_res.storage_path, 3600)
        if isinstance(url_res, dict):
            download_url = url_res.get("signedURL", url_res.get("signed_url", ""))
        elif hasattr(url_res, "signed_url"):
            download_url = url_res.signed_url
    except Exception:
        logger.warning("Failed to create signed URL for %s", gen_res.storage_path)

    # Audit log
    try:
        db.table("audit_log").insert({
            "firm_id": str(current_user.firm_id),
            "action": "generate_cma",
            "entity_type": "cma_project",
            "entity_id": project_id,
            "metadata": {
                "file_name": gen_res.file_name,
                "version": gen_res.version,
                "generation_time_ms": gen_res.generation_time_ms,
            },
        }).execute()
    except Exception:
        logger.warning("Failed to write audit log for generation")

    return StandardResponse(data={
        "success": True,
        "file_id": gen_res.generated_file_id,
        "file_name": gen_res.file_name,
        "file_size": gen_res.file_size,
        "version": gen_res.version,
        "download_url": download_url,
        "validation_passed": gen_res.validation.passed if gen_res.validation else True,
        "generation_time_ms": gen_res.generation_time_ms,
    })
