from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date
from .base import BaseResponse, BaseCreate, BaseUpdate

class CustomerCreate(BaseCreate):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    notes: Optional[str] = None
    is_vip: bool = False

class CustomerUpdate(BaseUpdate):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    notes: Optional[str] = None
    is_vip: Optional[bool] = None

class CustomerResponse(BaseResponse):
    name: str
    email: Optional[str]
    phone: Optional[str]
    cpf_cnpj: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    birth_date: Optional[date]
    notes: Optional[str]
    is_vip: bool
