from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class ProjectCreate(BaseModel):
    client_id: UUID
    financial_year: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    bank_name: Optional[str] = None
    loan_type: Optional[Literal['term_loan', 'working_capital', 'cc_od', 'other']] = None
    loan_amount: Optional[float] = None

class ProjectUpdate(BaseModel):
    bank_name: Optional[str] = None
    loan_type: Optional[Literal['term_loan', 'working_capital', 'cc_od', 'other']] = None
    loan_amount: Optional[float] = None

class ProjectResponse(BaseModel):
    id: UUID
    firm_id: UUID
    client_id: UUID
    financial_year: str
    bank_name: Optional[str] = None
    loan_type: Optional[str] = None
    loan_amount: Optional[float] = None
    status: str
    extracted_data: Optional[dict] = None
    classification_results: Optional[dict] = None
    validation_errors: Optional[dict] = None
    pipeline_progress: int
    pipeline_current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    # Extra fields
    client_name: str
    client_entity_type: str
    uploaded_file_count: int = 0
    review_pending_count: int = 0

class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    per_page: int
