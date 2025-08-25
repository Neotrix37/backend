from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from decimal import Decimal
from enum import Enum
from .base import BaseResponse, BaseCreate, BaseUpdate

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário para login")
    email: Optional[EmailStr] = Field(None, description="E-mail do usuário")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nome completo do usuário")
    
    # Permissões
    role: UserRole = Field(UserRole.VIEWER, description="Nível de acesso do usuário")
    is_active: bool = Field(True, description="Indica se o usuário está ativo")
    can_supply: bool = Field(False, description="Pode abastecer produtos")
    
    # Compatibilidade com frontend
    is_admin: Optional[bool] = Field(False, description="(Frontend) Indica se é administrador")
    salary: Optional[Decimal] = Field(None, ge=0, description="Salário do usuário")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: str(v) if v is not None else None
        }

class UserCreate(UserBase, BaseCreate):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=6, max_length=100, description="Senha do usuário")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "joao.silva",
                "password": "senha123",
                "full_name": "João da Silva",
                "email": "joao@empresa.com",
                "role": "cashier",
                "is_active": True,
                "can_supply": True,
                "salary": 2000.00
            }
        }

class UserUpdate(UserBase, BaseUpdate):
    """Schema para atualização de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Nova senha (opcional)")
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "João da Silva Santos",
                "email": "joao.novo@empresa.com",
                "role": "manager",
                "is_active": True,
                "can_supply": True,
                "salary": 2500.00
            }
        }

class UserResponse(UserBase, BaseResponse):
    """Schema para resposta da API"""
    id: int
    
    class Config:
        orm_mode = True

class UserInDB(UserResponse):
    """Schema para usuário no banco de dados"""
    hashed_password: str

class UserLogin(BaseModel):
    """Schema para login"""
    username: str = Field(..., description="Nome de usuário")
    password: str = Field(..., description="Senha")

class Token(BaseModel):
    """Schema para token de autenticação"""
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    """Schema para dados do token"""
    username: Optional[str] = None
