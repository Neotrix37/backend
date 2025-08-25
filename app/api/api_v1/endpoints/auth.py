from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_active_user,
    create_tokens_for_user,
    set_auth_cookies,
    clear_auth_cookies,
    require_role
)
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    Token, 
    TokenRefresh,
    UserLogin
)

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

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Registra um novo usuário no sistema
    
    - **username**: Nome de usuário único
    - **email**: Email do usuário (opcional)
    - **password**: Senha do usuário (mínimo 6 caracteres)
    - **full_name**: Nome completo do usuário
    - **role**: Função do usuário (padrão: viewer)
    - **is_admin**: Se o usuário é administrador (opcional, para compatibilidade com desktop)
    """
    # Verificar se já existe usuário com o mesmo username
    existing_user = db.query(User).filter(
        User.username == user_data.username,
        User.is_active == True
    ).first()
    
    if existing_user:
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um usuário com este email"
            )
    
    # Criar hash da senha
    hashed_password = get_password_hash(user_data.password)
    
    # Criar usuário
    user_dict = user_data.model_dump(exclude={"password", "is_admin"}, exclude_unset=True)
    
    # Mapear campos do desktop (compatibilidade)
    if hasattr(user_data, 'is_admin') and user_data.is_admin:
        user_dict["role"] = UserRole.ADMIN
        user_dict["is_superuser"] = True
    
    # Garantir que a senha seja armazenada com hash
    user_dict["hashed_password"] = hashed_password
    
    new_user = User(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    Autentica um usuário e retorna um token JWT
    
    - **username**: Nome de usuário
    - **password**: Senha do usuário
    """
    # Buscar usuário no banco
    user = db.query(User).filter(
        User.username == form_data.username,
        User.is_active == True
    ).first()
    
    # Verificar se usuário existe e senha está correta
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar tokens de acesso e atualização
    access_token, refresh_token = create_tokens_for_user(user, db)
    
    # Configurar cookies de autenticação
    set_auth_cookies(response, access_token, refresh_token)
    
    # Converter o modelo SQLAlchemy para Pydantic
    user_response = UserResponse.from_orm(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_response
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Gera um novo access token a partir de um refresh token
    """
    from jose import jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de atualização inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar o refresh token
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar se é um refresh token
        if payload.get("type") != "refresh":
            raise credentials_exception
            
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if not username or not user_id:
            raise credentials_exception
            
        # Buscar usuário no banco
        user = db.query(User).filter(
            User.username == username,
            User.id == user_id,
            User.refresh_token == refresh_data.refresh_token,
            User.is_active == True
        ).first()
        
        if not user:
            raise credentials_exception
            
        # Criar novos tokens
        access_token, refresh_token = create_tokens_for_user(user, db)
        
        # Atualizar cookies
        set_auth_cookies(response, access_token, refresh_token)
        
        # Converter o modelo SQLAlchemy para Pydantic
        user_response = UserResponse.from_orm(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_response
        }
        
    except Exception as e:
        raise credentials_exception

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Invalida o refresh token do usuário e limpa os cookies
    """
    # Invalidar o refresh token
    current_user.refresh_token = None
    db.commit()
    
    # Limpar cookies de autenticação
    clear_auth_cookies(response)
    
    return {"message": "Logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retorna as informações do usuário atualmente autenticado
    """
    return current_user

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Altera a senha do usuário atual
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha (mínimo 6 caracteres)
    """
    # Verificar a senha atual
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualizar a senha
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}
