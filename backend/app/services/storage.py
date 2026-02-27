from app.db.supabase_client import get_supabase
from datetime import datetime

def upload_file(firm_id: str, project_id: str, file_name: str, file_bytes: bytes, content_type: str) -> str:
    """
    Upload a file to Supabase storage.
    Returns the storage path.
    """
    db = get_supabase()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = file_name.replace(" ", "_")
    storage_path = f"{firm_id}/{project_id}/{timestamp}_{safe_filename}"

    db.storage.from_("cma-files").upload(
        file=file_bytes,
        path=storage_path,
        file_options={"content-type": content_type}
    )

    return storage_path

def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Get a temporary download URL for a file in Supabase storage.
    """
    db = get_supabase()
    res = db.storage.from_("cma-files").create_signed_url(storage_path, expires_in)
    
    # Supabase Python client returns a dict with 'signedURL'
    if isinstance(res, dict) and 'signedURL' in res:
         return res['signedURL']
         
    # Handle possible return types depending on supabase-py version
    if hasattr(res, 'signedURL'):
        return res.signedURL
        
    # In older versions or specific setups, the response might be structured differently
    # Standard format for latest versions is usually res['signedURL']
    return res.get('signedURL', '') if isinstance(res, dict) else str(res)

def delete_file(storage_path: str):
    """
    Delete a file from Supabase storage.
    """
    db = get_supabase()
    db.storage.from_("cma-files").remove([storage_path])
