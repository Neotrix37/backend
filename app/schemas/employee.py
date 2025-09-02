from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from decimal import Decimal
from .base import BaseResponse, BaseCreate, BaseUpdate

class EmployeeCreate(BaseCreate):
    full_name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    salary: Optional[Decimal] = Field(None, ge=0)
    
    # Permissões
    is_admin: bool = False
    can_sell: bool = True
    can_manage_inventory: bool = False
    can_manage_expenses: bool = False
    
    @field_validator('username')
    def username_must_start_with_uppercase(cls, v):
        if v[0].islower():
            raise ValueError('O nome de usuário deve começar com letra maiúscula')
        return v

class EmployeeUpdate(BaseUpdate):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    salary: Optional[Decimal] = Field(None, ge=0)
    
    # Permissões
    is_admin: Optional[bool] = None
    can_sell: Optional[bool] = None
    can_manage_inventory: Optional[bool] = None
    can_manage_expenses: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @field_validator('username')
    def username_must_start_with_uppercase(cls, v):
        if v is not None and v[0].islower():
            raise ValueError('O nome de usuário deve começar com letra maiúscula')
        return v

class EmployeeResponse(BaseResponse):
    full_name: str
    username: str
    salary: Optional[Decimal]
    is_admin: bool
    can_sell: bool
    can_manage_inventory: bool
    can_manage_expenses: bool
    is_active: bool

    class Config:
        from_attributes = True
