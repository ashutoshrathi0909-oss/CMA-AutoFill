from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID

class FileResponse(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    file_size: int
    document_type: Optional[str] = None
    extraction_status: str
    storage_path: str
    uploaded_by: Optional[UUID] = None
    created_at: datetime

class FileListResponse(BaseModel):
    items: list[FileResponse]
    
class GeneratedFileResponse(BaseModel):
    id: UUID
    file_name: str
    file_size: Optional[int] = None
    version: int
    storage_path: str
    generated_at: datetime

class GeneratedFileListResponse(BaseModel):
    items: list[GeneratedFileResponse]
