from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from decimal import Decimal
from datetime import date

from app.core.config import settings
from app.core.database import get_db
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, TokenData, 
    UserPermissions, UserInfo, TokenResponse
)
from app.models.user import User, UserRole  # Removido import do modelo UserModel
from app.models.employee import Employee  # Adicionado import do modelo Employee

router = APIRouter()

# Configurações de segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Permissões por papel (role)
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "can_manage_products": True,
        "can_manage_categories": True,
        "can_manage_sales": True,
        "can_view_all_sales": True,
        "can_manage_employees": True,
        "can_manage_inventory": True,
        "can_view_reports": True,
        "can_manage_expenses": True,
        "can_close_register": True,
        "can_manage_system_settings": True
    },
    UserRole.MANAGER: {
        "can_manage_products": True,
        "can_manage_categories": True,
        "can_manage_sales": True,
        "can_view_all_sales": True,
        "can_manage_employees": False,
        "can_manage_inventory": True,
        "can_view_reports": True,
        "can_manage_expenses": True,
        "can_close_register": True,
        "can_manage_system_settings": False
    },
    UserRole.CASHIER: {
        "can_manage_products": False,
        "can_manage_categories": False,
        "can_manage_sales": True,
        "can_view_all_sales": False,
        "can_manage_employees": False,
        "can_manage_inventory": False,
        "can_view_reports": False,
        "can_manage_expenses": False,
        "can_close_register": True,
        "can_manage_system_settings": False
    },
    UserRole.VIEWER: {
        "can_manage_products": False,
        "can_manage_categories": False,
        "can_manage_sales": False,
        "can_view_all_sales": True,
        "can_manage_employees": False,
        "can_manage_inventory": False,
        "can_view_reports": True,
        "can_manage_expenses": False,
        "can_close_register": False,
        "can_manage_system_settings": False
    }
}

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

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        print("Erro: Nenhum token fornecido")
        raise credentials_exception
    
    try:
        # Print the token for debugging (remove in production)
        print(f"Validando token: {token[:20]}...")
        
        # Decode the token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}  # Ensure expiration is verified
        )
        
        print(f"Token payload: {payload}")
        
        username: str = payload.get("sub")
        is_employee: bool = payload.get("is_employee", False)
        
        if not username:
            print("Erro: Nenhum nome de usuário encontrado no token")
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        print("Erro: Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        print(f"Erro na validação do token: {str(e)}")
        raise credentials_exception
    except Exception as e:
        print(f"Erro inesperado ao validar token: {str(e)}")
        raise credentials_exception
    
    # Se for um funcionário, buscar na tabela employees
    if is_employee:
        user = db.query(Employee).filter(
            Employee.username == username, 
            Employee.is_active == True
        ).first()
        
        if user is None:
            raise credentials_exception
            
        return {
            "username": user.username,
            "email": "",
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_employee": True,
            "permissions": {
                "can_manage_products": user.has_permission("can_manage_products"),
                "can_manage_categories": user.has_permission("can_manage_categories"),
                "can_manage_sales": user.has_permission("can_manage_sales"),
                "can_view_all_sales": user.has_permission("can_view_all_sales"),
                "can_manage_employees": user.has_permission("can_manage_employees"),
                "can_manage_inventory": user.has_permission("can_manage_inventory"),
                "can_view_reports": user.has_permission("can_view_reports"),
                "can_manage_expenses": user.has_permission("can_manage_expenses"),
                "can_close_register": user.has_permission("can_close_register"),
                "can_manage_system_settings": user.has_permission("can_manage_system_settings")
            }
        }
    
    # Se não for um funcionário, buscar na tabela users
    user = db.query(User).filter(
        User.username == username, 
        User.is_active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return {
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_employee": False,
        "permissions": {
            "can_manage_products": has_permission(user, "can_manage_products"),
            "can_manage_categories": has_permission(user, "can_manage_categories"),
            "can_manage_sales": has_permission(user, "can_manage_sales"),
            "can_view_all_sales": has_permission(user, "can_view_all_sales"),
            "can_manage_employees": has_permission(user, "can_manage_employees"),
            "can_manage_inventory": has_permission(user, "can_manage_inventory"),
            "can_view_reports": has_permission(user, "can_view_reports"),
            "can_manage_expenses": has_permission(user, "can_manage_expenses"),
            "can_close_register": has_permission(user, "can_close_register"),
            "can_manage_system_settings": has_permission(user, "can_manage_system_settings")
        }
    }

# Função auxiliar para verificar permissões
def has_permission(user: User, permission: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    if not user or not user.role:
        return False
    return ROLE_PERMISSIONS.get(user.role, {}).get(permission, False)

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
            role=UserRole.ADMIN if is_admin else UserRole.CASHIER,  # Define como CASHIER se não for admin
            is_superuser=is_admin,
            is_active=True,
            salary=Decimal('1500.00')  # Valor padrão explícito
        )
        
        print(f"📝 Criando novo usuário no banco de dados: {db_user}")
        
        # Adicionar e commitar o usuário
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Se o usuário for um CASHIER, criar um registro de funcionário correspondente
        if db_user.role == UserRole.CASHIER:
            try:
                print(f"🔄 Criando registro de funcionário para o usuário {db_user.id}")
                
                # Extrair primeiro e último nome do full_name
                name_parts = db_user.full_name.strip().split()
                first_name = name_parts[0] if name_parts else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                # Criar funcionário com dados básicos
                employee = Employee(
                    name=db_user.full_name,
                    email=db_user.email,
                    cpf="000.000.000-00",  # CPF padrão, deve ser atualizado posteriormente
                    position="Atendente",  # Cargo padrão
                    department="Vendas",   # Departamento padrão
                    hire_date=date.today(),  # Data de contratação atual
                    salary=db_user.salary,  # Mesmo salário do usuário
                    address="",            # Endereço vazio por padrão
                    city="",               # Cidade vazia por padrão
                    state="",              # Estado vazio por padrão
                    zip_code="",           # CEP vazio por padrão
                    is_active=True,        # Ativo por padrão
                    can_sell=True          # Pode realizar vendas
                )
                
                db.add(employee)
                db.commit()
                db.refresh(employee)
                
                print(f"✅ Funcionário criado com sucesso! ID: {employee.id}")
                
                # Atualizar o usuário com o ID do funcionário (se necessário)
                # db_user.employee_id = employee.id
                # db.commit()
                # db.refresh(db_user)
                
            except Exception as emp_error:
                # Se der erro ao criar o funcionário, apenas loga o erro e continua
                # Não falha o registro do usuário por causa disso
                error_type = type(emp_error).__name__
                error_detail = str(emp_error)
                print(f"⚠️ AVISO: Não foi possível criar registro de funcionário: {error_detail} (Tipo: {error_type})")
        
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

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    # Primeiro tenta encontrar o usuário na tabela users
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Se não encontrar, tenta na tabela employees
    if not user:
        employee = db.query(Employee).filter(Employee.username == form_data.username).first()
        if employee and verify_password(form_data.password, employee.password_hash):
            if not employee.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Conta de funcionário inativa"
                )
            
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": employee.username, "is_employee": True}, 
                expires_delta=access_token_expires
            )
            
            permissions = {
                "can_manage_products": employee.has_permission("can_manage_products"),
                "can_manage_categories": employee.has_permission("can_manage_categories"),
                "can_manage_sales": employee.has_permission("can_manage_sales"),
                "can_view_all_sales": employee.has_permission("can_view_all_sales"),
                "can_manage_employees": employee.has_permission("can_manage_employees"),
                "can_manage_inventory": employee.has_permission("can_manage_inventory"),
                "can_view_reports": employee.has_permission("can_view_reports"),
                "can_manage_expenses": employee.has_permission("can_manage_expenses"),
                "can_close_register": employee.has_permission("can_close_register"),
                "can_manage_system_settings": employee.has_permission("can_manage_system_settings")
            }
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": int(access_token_expires.total_seconds()),
                "user": {
                    "username": employee.username,
                    "email": "",
                    "full_name": employee.full_name,
                    "role": employee.role,
                    "is_active": employee.is_active,
                    "is_employee": True,
                    "permissions": permissions
                }
            }
    
    # Verificação para usuário normal
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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_employee": False}, 
        expires_delta=access_token_expires
    )
    
    permissions = {
        "can_manage_products": has_permission(user, "can_manage_products"),
        "can_manage_categories": has_permission(user, "can_manage_categories"),
        "can_manage_sales": has_permission(user, "can_manage_sales"),
        "can_view_all_sales": has_permission(user, "can_view_all_sales"),
        "can_manage_employees": has_permission(user, "can_manage_employees"),
        "can_manage_inventory": has_permission(user, "can_manage_inventory"),
        "can_view_reports": has_permission(user, "can_view_reports"),
        "can_manage_expenses": has_permission(user, "can_manage_expenses"),
        "can_close_register": has_permission(user, "can_close_register"),
        "can_manage_system_settings": has_permission(user, "can_manage_system_settings")
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "is_employee": False,
            "permissions": permissions
        }
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
