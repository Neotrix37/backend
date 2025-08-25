from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum

from .base import BaseResponse, BaseCreate, BaseUpdate

class UserRole(str, Enum):
    """Funções de usuário disponíveis no sistema"""
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    SUPPLIER = "supplier"
    VIEWER = "viewer"

class UserBase(BaseModel):
    """Modelo base para usuário"""
    username: str = Field(..., min_length=3, max_length=50, example="joaosilva")
    email: Optional[EmailStr] = Field(
        None, 
        example="usuario@exemplo.com"
    )
    full_name: str = Field(..., min_length=2, max_length=100, example="João da Silva")
    role: UserRole = Field(default=UserRole.VIEWER, example="cashier")
    is_active: bool = Field(default=True, description="Indica se o usuário está ativo")
    is_superuser: bool = Field(default=False, description="Indica se o usuário tem privilégios de superusuário")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "joaosilva",
                "email": "joao@exemplo.com",
                "full_name": "João da Silva",
                "role": "cashier",
                "is_active": True,
                "is_superuser": False
            }
        }

class UserCreate(UserBase, BaseCreate):
    """Esquema para criação de usuário"""
    password: str = Field(..., min_length=6, max_length=100, example="senhasegura123")
    
    # Compatibilidade com desktop (Flet)
    is_admin: Optional[bool] = Field(
        None, 
        description="Campo de compatibilidade - define se o usuário é administrador"
    )
    
    @root_validator(pre=True)
    def set_admin_role(cls, values):
        """Define a função de admin se is_admin for True"""
        is_admin = values.get('is_admin')
        if is_admin:
            values['role'] = UserRole.ADMIN
            values['is_superuser'] = True
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "username": "novousuario",
                "email": "novo@exemplo.com",
                "full_name": "Novo Usuário",
                "password": "senhasegura123",
                "role": "cashier",
                "is_admin": False
            }
        }

class UserUpdate(UserBase, BaseUpdate):
    """Esquema para atualização de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=6, description="Nova senha (opcional)")
    current_password: Optional[str] = Field(
        None, 
        min_length=6, 
        description="Senha atual (obrigatória para alteração de senha)"
    )
    
    # Remover campos que não devem ser atualizáveis diretamente
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
    @root_validator
    def validate_password_change(cls, values):
        """Valida a alteração de senha"""
        password = values.get('password')
        current_password = values.get('current_password')
        
        if password and not current_password:
            raise ValueError("A senha atual é necessária para alterar a senha")
            
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Novo Nome",
                "email": "novoemail@exemplo.com"
            }
        }

class UserResponse(UserBase, BaseResponse):
    """Resposta da API para dados do usuário"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "joaosilva",
                "email": "joao@exemplo.com",
                "full_name": "João da Silva",
                "role": "cashier",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "last_login": "2023-01-01T12:00:00"
            }
        }

class UserInDB(UserResponse):
    """Modelo para usuário no banco de dados"""
    hashed_password: str
    refresh_token: Optional[str] = None
    token_version: int = 0

class UserLogin(BaseModel):
    """Esquema para autenticação de usuário"""
    username: str = Field(..., example="joaosilva")
    password: str = Field(..., example="senhasegura123")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "joaosilva",
                "password": "senhasegura123"
            }
        }

class Token(BaseModel):
    """Resposta de autenticação com token JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutos em segundos
    user: UserResponse
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "joaosilva",
                    "email": "joao@exemplo.com",
                    "full_name": "João da Silva",
                    "role": "cashier",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00",
                    "last_login": "2023-01-01T12:00:00"
                }
            }
        }

class TokenRefresh(BaseModel):
    """Esquema para solicitação de refresh token"""
    refresh_token: str
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }

class TokenData(BaseModel):
    """Dados armazenados no token JWT"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None
    is_superuser: bool = False
    permissions: List[str] = []
    type: str = "access"  # access, refresh, etc.
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None  # ID único do token
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp()) if v else None
        }

class PasswordResetRequest(BaseModel):
    """Solicitação de redefinição de senha"""
    email: EmailStr
    
    class Config:
        schema_extra = {
            "example": {
                "email": "usuario@exemplo.com"
            }
        }

class PasswordResetConfirm(BaseModel):
    """Confirmação de redefinição de senha"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)
    
    class Config:
        schema_extra = {
            "example": {
                "token": "token-unico-gerado-para-recuperacao",
                "new_password": "novasenha123"
            }
        }
