from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import CurrentUser
from app.models.response import StandardResponse
from app.db.supabase_client import get_supabase

router = APIRouter()

@router.get("/me", response_model=StandardResponse[dict])
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    db = get_supabase()
    
    # Fetch firm info
    try:
        response = db.table("firms").select("id, name, plan").eq("id", current_user.firm_id).execute()
        firm_data = response.data[0] if response.data else None
    except Exception:
        firm_data = {"id": str(current_user.firm_id), "name": "Unknown", "plan": "unknown"}
        
    user_info = {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "firm": firm_data
    }
    
    return StandardResponse(data=user_info)
