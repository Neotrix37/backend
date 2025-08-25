from sqlalchemy import Column, String, Boolean, Enum, Numeric
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

class User(BaseModel):
    """Modelo para usuários do sistema"""
    __tablename__ = "users"
    
    # Dados de autenticação
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Dados básicos
    full_name = Column(String(100), nullable=False)
    
    # Permissões e status
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Compatibilidade com frontend
    can_supply = Column(Boolean, default=False, nullable=False)  # Pode abastecer produtos
    salary = Column(Numeric(10, 2), nullable=True)  # Salário (opcional)
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
