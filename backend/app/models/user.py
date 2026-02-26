from uuid import UUID
from pydantic import BaseModel

class CurrentUser(BaseModel):
    id: UUID
    firm_id: UUID
    email: str
    full_name: str
    role: str
