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
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
