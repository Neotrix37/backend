from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from decimal import Decimal

from app.core.config import settings
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.models.user import User, UserRole

router = APIRouter()

# Configurações de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Funções auxiliares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Registrar novo usuário
    """
    try:
        print(f"\n=== INÍCIO DO REGISTRO ===")
        print(f"Tentando registrar usuário: {user_data.username}")
        print(f"Email: {user_data.email}")
        print(f"Nome completo: {user_data.full_name}")
        print(f"É admin: {getattr(user_data, 'is_admin', False)}")
        
        # Verificar se já existe usuário com o mesmo username
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.is_active == True
        ).first()
        
        if existing_user:
            print(f"❌ ERRO: Já existe um usuário ativo com o username: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este username"
            )
        
        # Verificar se já existe usuário com o mesmo email
        if user_data.email:
            existing_email = db.query(User).filter(
                User.email == user_data.email,
                User.is_active == True
            ).first()
            
            if existing_email:
                print(f"❌ ERRO: Já existe um usuário ativo com o email: {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um usuário com este email"
                )
        
        # Criar hash da senha
        hashed_password = get_password_hash(user_data.password)
        print("✅ Hash da senha criado com sucesso")
        
        # Definir role e is_superuser baseado em is_admin
        is_admin = getattr(user_data, 'is_admin', False)
        
        # Criar objeto de usuário com valor padrão para salary
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN if is_admin else UserRole.VIEWER,
            is_superuser=is_admin,
            is_active=True,
            salary=Decimal('1500.00')  # Valor padrão explícito
        )
        
        print(f"📝 Criando novo usuário no banco de dados: {db_user}")
        
        # Adicionar e commitar o usuário
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ Usuário criado com sucesso! ID: {db_user.id}")
        return db_user
        
    except Exception as e:
        db.rollback()
        error_type = type(e).__name__
        error_detail = str(e)
        print(f"❌ ERRO ao criar usuário: {error_detail}. Tipo: {error_type}")
        print(f"=== FIM DO REGISTRO COM ERRO ===\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {error_detail}"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Any:
    """Login do usuário"""
    print(f"Tentativa de login para o usuário: {form_data.username}")
    
    # Buscar usuário no banco
    user = db.query(User).filter(
        User.username == form_data.username,
        User.is_active == True
    ).first()
    
    if not user:
        print(f"Usuário não encontrado ou inativo: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Usuário encontrado: {user.username}, Hash armazenado: {user.hashed_password[:20]}...")
    
    # Verificar senha
    if not verify_password(form_data.password, user.hashed_password):
        print("Senha incorreta")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Login bem-sucedido para o usuário: {user.username}")
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """Obter informações do usuário atual"""
    return current_user
