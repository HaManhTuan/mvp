from typing import Optional, List, Generic, TypeVar, Type
from pydantic import BaseModel, Field
from datetime import datetime

# Generic type for data models
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema for all Pydantic models"""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class ResponseBase(BaseSchema, Generic[T]):
    """Base response schema"""
    success: bool = True
    message: str = "Operation successful"
    
    
class DataResponse(ResponseBase[T]):
    """Response schema with data"""
    data: Optional[T] = None
    
    
class ListResponse(ResponseBase[T]):
    """Response schema with paginated list of data"""
    data: List[T] = []
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    
class ErrorResponse(ResponseBase[T]):
    """Error response schema"""
    success: bool = False
    message: str = "An error occurred"
    error_code: Optional[str] = None
    details: Optional[dict] = None
