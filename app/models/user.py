from sqlalchemy import Column, String, Boolean, Enum, Numeric
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
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)  # Campo de salário adicionado
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="user")
    
    def set_password(self, password: str):
        """Set hashed password"""
        self.hashed_password = get_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return verify_password(password, self.hashed_password)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role}, is_active={self.is_active})>"
