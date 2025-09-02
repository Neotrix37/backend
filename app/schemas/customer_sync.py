from datetime import date
from typing import Optional
from pydantic import Field, EmailStr
from .base import BaseCreate

class CustomerSyncResponse(BaseCreate):
    """Schema específico para resposta de sincronização de clientes"""
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    notes: Optional[str] = None
    is_vip: bool = False
    
    class Config:
        populate_by_name = True
        from_attributes = True