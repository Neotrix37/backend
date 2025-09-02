from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from .base import BaseCreate

class EmployeeSyncResponse(BaseCreate):
    """Schema específico para resposta de sincronização de funcionários"""
    full_name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=3, max_length=50)
    salary: Optional[Decimal] = Field(None, ge=0)
    
    # Permissões
    is_admin: bool = False
    can_sell: bool = True
    can_manage_inventory: bool = False
    can_manage_expenses: bool = False
    is_active: bool = True
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
        }