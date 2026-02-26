from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ErrorInfo(BaseModel):
    message: str
    code: Optional[str] = None

class StandardResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorInfo] = None
