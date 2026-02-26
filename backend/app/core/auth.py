import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt
from app.models.user import CurrentUser
from app.db.supabase_client import get_supabase

# Supabase Auth expects Bearer token
security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    db: Client = get_supabase()
    
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    try:
        user_id = None
        if jwt_secret:
            # Decode locally if secret is provided in .env
            payload = jwt.decode(
                token, 
                jwt_secret, 
                algorithms=["HS256"], 
                options={"verify_aud": False}
            )
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("No 'sub' in token")
        else:
            # Fallback to Supabase Auth API
            auth_response = db.auth.get_user(token)
            if not auth_response or not auth_response.user:
                raise ValueError("Invalid user token")
            user_id = auth_response.user.id
            
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Query the users table for firm_id, role, etc.
    try:
        response = db.table("users").select("id, firm_id, email, full_name, role, is_active").eq("id", user_id).execute()
    except Exception as e:
        # DB Error or something went wrong fetching the user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating user permissions: {e}"
        )
        
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_data = response.data[0]
    
    # Check if deactivated
    if not user_data.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
        
    return CurrentUser(
        id=user_data["id"],
        firm_id=user_data["firm_id"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        role=user_data["role"]
    )

def require_role(allowed_roles: list[str]):
    """
    Dependency to enforce role-based access control.
    Example: @app.get("/admin", dependencies=[Depends(require_role(["owner", "ca"]))])
    """
    def role_dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not allowed to access this resource"
            )
        return current_user
    return role_dependency
