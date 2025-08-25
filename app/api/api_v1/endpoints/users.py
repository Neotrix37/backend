from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    UserInDB, UserLogin, Token, TokenData
)
from app.core.security import (
    get_password_hash, 
    verify_password,
    create_access_token,
    get_current_active_user
)
from app.core.pagination import Page, paginate

router = APIRouter()

@router.get("/", response_model=Page[UserResponse])
async def list_users(
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    can_supply: Optional[bool] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Lista todos os usuários com paginação e filtros
    """
    # Verifica permissão
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    query = select(User)
    
    # Aplica filtros
    if search:
        search = f"%{search}%"
        query = query.where(
            or_(
                User.full_name.ilike(search),
                User.username.ilike(search),
                User.email.ilike(search) if User.email is not None else False
            )
        )
    
    if role:
        query = query.where(User.role == role)
        
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        
    if can_supply is not None:
        query = query.where(User.can_supply == can_supply)
    
    # Ordena por nome
    query = query.order_by(User.full_name)
    
    return paginate(db, query, page, size)

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna os dados do usuário atual
    """
    return current_user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cria um novo usuário
    """
    # Verifica permissão
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar usuários"
        )
    
    # Verifica se o username já existe
    existing_user = db.scalar(select(User).where(User.username == user_in.username))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um usuário com este username"
        )
    
    # Verifica se o email já existe
    if user_in.email:
        existing_email = db.scalar(select(User).where(User.email == user_in.email))
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este e-mail"
            )
    
    # Cria o usuário
    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.dict(exclude={"password"}, exclude_unset=True)
    
    # Converte is_admin para role se necessário (compatibilidade com frontend)
    if user_data.get("is_admin"):
        user_data["role"] = UserRole.ADMIN
    
    db_user = User(
        **user_data,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna os dados de um usuário específico
    """
    # Verifica permissão
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Atualiza um usuário existente
    """
    # Verifica permissão
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    db_user = db.get(User, user_id)
    if not db_user or not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica se o novo username já existe
    if user_in.username and user_in.username != db_user.username:
        existing_user = db.scalar(select(User).where(User.username == user_in.username))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este username"
            )
    
    # Verifica se o novo email já existe
    if user_in.email and user_in.email != db_user.email:
        existing_email = db.scalar(select(User).where(User.email == user_in.email))
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este e-mail"
            )
    
    # Atualiza os campos
    update_data = user_in.dict(exclude_unset=True, exclude={"password"})
    
    # Atualiza a senha se fornecida
    if user_in.password:
        update_data["hashed_password"] = get_password_hash(user_in.password)
    
    # Converte is_admin para role se necessário (compatibilidade com frontend)
    if "is_admin" in update_data:
        update_data["role"] = UserRole.ADMIN if update_data["is_admin"] else UserRole.VIEWER
        del update_data["is_admin"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Remove um usuário (soft delete)
    """
    # Verifica permissão
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover usuários"
        )
    
    # Impede que o próprio usuário se remova
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode remover seu próprio usuário"
        )
    
    db_user = db.get(User, user_id)
    if not db_user or not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Soft delete
    db_user.is_active = False
    db_user.updated_at = datetime.utcnow()
    db.commit()
    
    return None

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Autentica um usuário e retorna um token de acesso
    """
    user = db.scalar(select(User).where(User.username == form_data.username))
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600  # 1 hora
    }
