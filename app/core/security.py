from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union, List, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import secrets
import string

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole

# Configuração do contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do esquema OAuth2 para autenticação via token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False  # Permite rotas públicas
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera um hash seguro para a senha fornecida"""
    return pwd_context.hash(password)

def generate_random_string(length: int = 32) -> str:
    """Gera uma string aleatória segura"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    Cria um token JWT com os dados fornecidos
    
    Args:
        data: Dados a serem incluídos no token
        expires_delta: Tempo de expiração do token
        token_type: Tipo do token (access, refresh, etc.)
    """
    to_encode = data.copy()
    
    # Definir tempo de expiração
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adicionar claims padrão
    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": generate_random_string(),
        "type": token_type
    })
    
    # Gerar o token JWT
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_token_from_request(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[str]:
    """Obtém o token da requisição, seja do header ou dos cookies"""
    if token:
        return token
    
    # Tentar obter o token do cookie
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        return token[7:]  # Remove 'Bearer '
    
    return None

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtém o usuário atual a partir do token JWT
    
    Retorna None se não houver token ou se for inválido
    """
    if not token:
        return None
    
    try:
        # Decodificar o token JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar o tipo do token
        token_type = payload.get("type")
        if token_type != "access":
            return None
            
        # Obter o username do token
        username: str = payload.get("sub")
        if not username:
            return None
            
        # Buscar o usuário no banco de dados
        user = db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
        
        if not user:
            return None
            
        # Armazenar o usuário no request.state para uso posterior
        request.state.user = user
        return user
        
    except JWTError:
        return None

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Verifica se o usuário está autenticado e ativo"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
        
    return current_user

# Funções de verificação de permissão
def require_role(required_roles: List[UserRole]):
    """
    Decorator para verificar se o usuário tem uma das funções necessárias
    
    Args:
        required_roles: Lista de funções permitidas
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para acessar este recurso"
            )
        return current_user
    return role_checker

# Funções de conveniência para papéis comuns
require_admin = require_role([UserRole.ADMIN])
require_manager = require_role([UserRole.ADMIN, UserRole.MANAGER])
require_cashier = require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER])
require_supplier = require_role([UserRole.ADMIN, UserRole.MANAGER, UserRole.SUPPLIER])

def create_tokens_for_user(
    user: User,
    db: Session
) -> Tuple[str, str]:
    """
    Cria um par de tokens (access e refresh) para o usuário
    
    Args:
        user: Instância do usuário
        db: Sessão do banco de dados
        
    Returns:
        Tuple com (access_token, refresh_token)
    """
    # Criar access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "role": user.role.value,
            "is_superuser": user.is_superuser,
            "permissions": ["read:profile", "update:profile"]
        },
        expires_delta=access_token_expires,
        token_type="access"
    )
    
    # Criar refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "token_version": user.token_version or 0
        },
        expires_delta=refresh_token_expires,
        token_type="refresh"
    )
    
    # Atualizar o refresh token no banco de dados
    user.refresh_token = refresh_token
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return access_token, refresh_token

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
) -> None:
    """
    Configura os cookies de autenticação na resposta
    
    Args:
        response: Objeto de resposta do FastAPI
        access_token: Token de acesso JWT
        refresh_token: Token de atualização JWT
    """
    secure = settings.SECURE_COOKIES
    
    # Configurar cookie de acesso
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    # Configurar cookie de refresh
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def clear_auth_cookies(response: Response) -> None:
    """Remove os cookies de autenticação"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
