from typing import Dict, Any, List
from datetime import datetime
from app.db.supabase_client import get_supabase

def merge_and_save_data(project_id: str, firm_id: str):
    db = get_supabase()
    
    files_resp = db.table("uploaded_files").select("file_name, extracted_data").eq("cma_project_id", project_id).eq("firm_id", firm_id).eq("extraction_status", "completed").execute()
    
    if not files_resp.data:
        return
        
    merged_data = {
        "profit_and_loss": None,
        "balance_sheet": None,
        "trial_balance": None,
        "metadata": {
            "source_files": [],
            "total_line_items": 0,
            "merged_at": datetime.now().isoformat() + "Z"
        }
    }
    
    total_items = 0
    all_files = []
    
    for row in files_resp.data:
        file_name = row["file_name"]
        extracted = row.get("extracted_data")
        if not extracted or not isinstance(extracted, dict):
            continue
            
        all_files.append(file_name)
        
        doc_type = extracted.get("document_type")
        if doc_type in ["profit_and_loss", "balance_sheet", "trial_balance"]:
            existing = merged_data[doc_type]
            
            # Simple dedup strategy: if one already exists, compare lengths and pick the longer one
            if existing:
                if len(extracted.get("line_items", [])) > len(existing.get("line_items", [])):
                    merged_data[doc_type] = {
                        "line_items": extracted.get("line_items", []),
                        "totals": extracted.get("totals", {})
                    }
                    total_items += len(extracted.get("line_items", [])) - len(existing.get("line_items", []))
            else:
                merged_data[doc_type] = {
                    "line_items": extracted.get("line_items", []),
                    "totals": extracted.get("totals", {})
                }
                total_items += len(extracted.get("line_items", []))
                
    merged_data["metadata"]["source_files"] = all_files
    merged_data["metadata"]["total_line_items"] = total_items
    
    # Save to project
    db.table("cma_projects").update({
        "status": "extracted",
        "pipeline_progress": 25,
        "extracted_data": merged_data
    }).eq("id", project_id).eq("firm_id", firm_id).execute()
    
    # Audit log
    db.table("audit_log").insert({
        "firm_id": firm_id,
        "action": "run_extraction",
        "entity_type": "cma_project",
        "entity_id": project_id,
        "metadata": {"files_processed": len(files_resp.data), "line_items_extracted": total_items}
    }).execute()
