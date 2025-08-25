from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Generic, Any
from datetime import datetime

T = TypeVar('T')

class BaseSchema(BaseModel):
    """Schema base com configurações comuns"""
    class Config:
        from_attributes = True
        json_encoders = {
            'decimal.Decimal': str,  # Convert Decimal to string in JSON
            'datetime': lambda v: v.isoformat()  # Format datetime as ISO string
        }

class BaseResponse(BaseSchema):
    """Base response model with common fields"""
    id: int = Field(..., description="Unique identifier")
    is_active: bool = Field(True, description="Whether the record is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class BaseCreate(BaseSchema):
    """Base model for creating new records"""
    is_active: bool = Field(True, description="Whether the record should be active")

class BaseUpdate(BaseSchema):
    """Base model for updating existing records"""
    is_active: Optional[bool] = Field(None, description="Set active/inactive status")
