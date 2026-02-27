import logging
from typing import Dict, Any
from datetime import datetime
from app.db.supabase_client import get_supabase

logger = logging.getLogger(__name__)

VALID_DOC_TYPES = ("profit_and_loss", "balance_sheet", "trial_balance")


def merge_and_save_data(project_id: str, firm_id: str) -> None:
    db = get_supabase()

    files_resp = (
        db.table("uploaded_files")
        .select("file_name, extracted_data")
        .eq("cma_project_id", project_id)
        .eq("firm_id", firm_id)
        .eq("extraction_status", "completed")
        .execute()
    )

    if not files_resp.data:
        return

    merged_data: Dict[str, Any] = {
        "profit_and_loss": None,
        "balance_sheet": None,
        "trial_balance": None,
        "metadata": {
            "source_files": [],
            "total_line_items": 0,
            "merged_at": datetime.now().isoformat() + "Z",
        },
    }

    total_items = 0
    all_files: list[str] = []

    for row in files_resp.data:
        file_name = row["file_name"]
        extracted = row.get("extracted_data")

        # Skip non-dict or error entries
        if not extracted or not isinstance(extracted, dict):
            continue
        if "error" in extracted and "line_items" not in extracted:
            logger.warning("Skipping errored file in merge: %s", file_name)
            continue

        all_files.append(file_name)

        doc_type = extracted.get("document_type")
        if doc_type not in VALID_DOC_TYPES:
            logger.info("File %s has doc_type '%s' — skipped in merge", file_name, doc_type)
            continue

        new_items = extracted.get("line_items", [])
        existing = merged_data[doc_type]

        if existing:
            old_count = len(existing.get("line_items", []))
            new_count = len(new_items)
            if new_count > old_count:
                logger.info("Replacing %s data: %s items → %s items", doc_type, old_count, new_count)
                merged_data[doc_type] = {
                    "line_items": new_items,
                    "totals": extracted.get("totals", {}),
                }
                total_items += new_count - old_count
            else:
                logger.info("Keeping existing %s data (%s items >= %s new)", doc_type, old_count, new_count)
        else:
            merged_data[doc_type] = {
                "line_items": new_items,
                "totals": extracted.get("totals", {}),
            }
            total_items += len(new_items)

    merged_data["metadata"]["source_files"] = all_files
    merged_data["metadata"]["total_line_items"] = total_items

    # Save to project
    db.table("cma_projects").update({
        "status": "extracted",
        "pipeline_progress": 25,
        "extracted_data": merged_data,
    }).eq("id", project_id).eq("firm_id", firm_id).execute()

    # Audit log
    try:
        db.table("audit_log").insert({
            "firm_id": firm_id,
            "action": "run_extraction",
            "entity_type": "cma_project",
            "entity_id": project_id,
            "metadata": {"files_processed": len(files_resp.data), "line_items_extracted": total_items},
        }).execute()
    except Exception as e:
        logger.warning("Failed to write audit log for merge: %s", e)
