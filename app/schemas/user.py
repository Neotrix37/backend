from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from decimal import Decimal
from enum import Enum
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

class UserCreate(BaseCreate):
    username: str = Field(..., min_length=3, max_length=50, example="marrapaz")
    email: Optional[EmailStr] = Field(None, example="usuario@exemplo.com")
    password: str = Field(..., min_length=6, example="senha123")
    full_name: str = Field(..., min_length=2, max_length=100, example="Nome Completo")
    role: Optional[UserRole] = Field(UserRole.VIEWER, example=UserRole.VIEWER)
    is_superuser: bool = Field(False, example=False)
    is_admin: bool = Field(False, example=True)
    salary: Optional[Decimal] = Field(None, example=1500.00)

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
        }
        json_schema_extra = {
            "example": {
                "username": "marrapaz",
                "email": "marrapaz@empresa.com",
                "password": "senha123",
                "full_name": "Usuário Marrapaz",
                "is_admin": True
            }
        }

class UserUpdate(BaseUpdate):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None
    # Atualização opcional de senha
    password: Optional[str] = Field(None, min_length=6)
    # Compatibilidade com desktop
    is_admin: Optional[bool] = None
    salary: Optional[Decimal] = None

class UserResponse(BaseResponse):
    username: str
    email: Optional[str]
    full_name: str
    role: UserRole
    is_superuser: bool
    salary: Optional[Decimal] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(round(float(v), 2)) if v is not None else None,
            datetime: lambda v: v.isoformat()
        }

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(UserResponse):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    is_employee: bool = False

class UserPermissions(BaseModel):
    can_manage_products: bool = False
    can_manage_categories: bool = False
    can_manage_sales: bool = False
    can_view_all_sales: bool = False
    can_manage_employees: bool = False
    can_manage_inventory: bool = False
    can_view_reports: bool = False
    can_manage_expenses: bool = False
    can_close_register: bool = False
    can_manage_system_settings: bool = False

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    is_employee: bool
    permissions: UserPermissions

class TokenResponse(Token):
    user: UserInfo
