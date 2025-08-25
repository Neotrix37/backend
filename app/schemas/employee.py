from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date
from decimal import Decimal
from .base import BaseResponse, BaseCreate, BaseUpdate

class EmployeeCreate(BaseCreate):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    cpf: str = Field(..., max_length=14)
    position: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    hire_date: date
    salary: Optional[Decimal] = Field(None, ge=0)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)
    can_sell: bool = True

class EmployeeUpdate(BaseUpdate):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = Field(None, ge=0)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)
    can_sell: Optional[bool] = None
    is_active: Optional[bool] = None

class EmployeeResponse(BaseResponse):
    name: str
    email: Optional[str]
    phone: Optional[str]
    cpf: str
    position: str
    department: Optional[str]
    hire_date: date
    salary: Optional[Decimal]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    can_sell: bool
