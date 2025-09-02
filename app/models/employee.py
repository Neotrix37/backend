from sqlalchemy import Column, String, Boolean, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user import User  # Importamos o User para o relacionamento

class Employee(BaseModel):
    """Modelo simplificado para funcionários do sistema"""
    __tablename__ = "employees"
    
    # Informações básicas
    full_name = Column(String(200), nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)
    
    # Permissões
    is_admin = Column(Boolean, default=False, nullable=False)
    can_sell = Column(Boolean, default=True, nullable=False)
    can_manage_inventory = Column(Boolean, default=False, nullable=False)
    can_manage_expenses = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="employee")
    sales = relationship("Sale", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(username={self.username}, is_admin={self.is_admin}>"
