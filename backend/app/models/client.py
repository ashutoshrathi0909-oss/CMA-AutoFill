from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1)
    entity_type: Literal['trading', 'manufacturing', 'service']
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    entity_type: Optional[Literal['trading', 'manufacturing', 'service']] = None
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class ClientBase(BaseModel):
    id: UUID
    firm_id: UUID
    name: str
    entity_type: str
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ClientResponse(ClientBase):
    cma_count: int = 0

class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    page: int
    per_page: int
