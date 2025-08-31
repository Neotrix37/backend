from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole, has_permission, ROLE_PERMISSIONS
from app.core.database import get_db

# Configuração do bcrypt para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_user_role(current_user: User = Depends(get_current_active_user)) -> UserRole:
    """Obtém a role do usuário atual"""
    return current_user.role

def has_role(required_roles: List[UserRole]):
    """Verifica se o usuário tem alguma das roles necessárias"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer uma das seguintes roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

def check_permission(permission: str):
    """Verifica se o usuário tem uma permissão específica"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada: {permission}"
            )
        return current_user
    return permission_checker

# Roles específicas
is_admin = has_role([UserRole.ADMIN])
is_manager_or_admin = has_role([UserRole.ADMIN, UserRole.MANAGER])
is_cashier = has_role([UserRole.CASHIER])
is_viewer = has_role([UserRole.VIEWER])

# Permissões específicas
can_manage_users = check_permission("can_manage_users")
can_manage_products = check_permission("can_manage_products")
can_manage_categories = check_permission("can_manage_categories")
can_manage_sales = check_permission("can_manage_sales")
can_view_all_sales = check_permission("can_view_all_sales")
can_manage_employees = check_permission("can_manage_employees")
can_manage_inventory = check_permission("can_manage_inventory")
can_view_reports = check_permission("can_view_reports")
can_manage_expenses = check_permission("can_manage_expenses")
can_close_register = check_permission("can_close_register")
can_manage_system_settings = check_permission("can_manage_system_settings")
