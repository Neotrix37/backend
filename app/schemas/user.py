from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from decimal import Decimal
from enum import Enum
from .base import BaseResponse, BaseCreate, BaseUpdate

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

class UserCreate(BaseCreate):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: Optional[UserRole] = UserRole.VIEWER
    is_superuser: Optional[bool] = False
    is_admin: bool = False
    salary: Optional[Decimal] = Field(None, ge=0)

    class Config:
        json_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
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
    salary: Optional[Decimal]

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
