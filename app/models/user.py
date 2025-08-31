from sqlalchemy import Column, String, Boolean, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import enum
from passlib.context import CryptContext
from .base import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

class UserRole(str, enum.Enum):
    ADMIN = "admin"        # Acesso total ao sistema
    MANAGER = "manager"    # Pode gerenciar produtos, categorias, vendas e funcionários (exceto admins)
    CASHIER = "cashier"    # Pode realizar vendas e ver suas próprias vendas
    VIEWER = "viewer"      # Apenas visualização

# Permissões específicas por papel
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "can_manage_users": True,
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
        "can_manage_users": False,
        "can_manage_products": True,
        "can_manage_categories": True,
        "can_manage_sales": True,
        "can_view_all_sales": True,
        "can_manage_employees": True,  # Mas não pode gerenciar outros gerentes ou admins
        "can_manage_inventory": True,
        "can_view_reports": True,
        "can_manage_expenses": True,
        "can_close_register": True,
        "can_manage_system_settings": False
    },
    UserRole.CASHIER: {
        "can_manage_users": False,
        "can_manage_products": False,
        "can_manage_categories": False,
        "can_manage_sales": False,
        "can_view_all_sales": False,  # Só vê as próprias vendas
        "can_manage_employees": False,
        "can_manage_inventory": False,
        "can_view_reports": False,
        "can_manage_expenses": False,
        "can_close_register": True,   # Pode fechar o próprio caixa
        "can_manage_system_settings": False
    },
    UserRole.VIEWER: {
        "can_manage_users": False,
        "can_manage_products": False,
        "can_manage_categories": False,
        "can_manage_sales": False,
        "can_view_all_sales": True,   # Pode ver todas as vendas (somente leitura)
        "can_manage_employees": False,
        "can_manage_inventory": False,
        "can_view_reports": True,     # Pode ver relatórios (somente leitura)
        "can_manage_expenses": False,
        "can_close_register": False,
        "can_manage_system_settings": False
    }
}

def has_permission(user: 'User', permission: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    if not user or not user.role:
        return False
    return ROLE_PERMISSIONS.get(user.role, {}).get(permission, False)

class User(BaseModel):
    """Modelo para usuários do sistema"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)  # Campo de salário adicionado
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
    employee = relationship("Employee", back_populates="user", uselist=False)
    
    def set_password(self, password: str):
        """Set hashed password"""
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return verify_password(password, self.hashed_password)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role}, is_active={self.is_active})>"
