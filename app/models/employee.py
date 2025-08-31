from sqlalchemy import Column, String, Boolean, Numeric, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user import User  # Importamos o User para o relacionamento

class EmployeeRole(str):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

    @classmethod
    def values(cls):
        return [cls.ADMIN, cls.MANAGER, cls.CASHIER, cls.VIEWER]

class Employee(BaseModel):
    """Modelo para funcionários do sistema com controle de acesso baseado em papéis"""
    __tablename__ = "employees"
    
    # Informações básicas
    full_name = Column(String(200), nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(*EmployeeRole.values(), name='employeerole'), 
                 default=EmployeeRole.CASHIER, 
                 nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="employee")
    sales = relationship("Sale", back_populates="employee")
    
    @property
    def is_admin(self):
        return self.role == EmployeeRole.ADMIN
    
    @property
    def is_manager(self):
        return self.role == EmployeeRole.MANAGER
    
    @property
    def is_cashier(self):
        return self.role == EmployeeRole.CASHIER
    
    @property
    def is_viewer(self):
        return self.role == EmployeeRole.VIEWER
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se o funcionário tem uma permissão específica"""
        from app.models.user import ROLE_PERMISSIONS
        return ROLE_PERMISSIONS.get(self.role, {}).get(permission, False)
    
    def __repr__(self):
        return f"<Employee(username={self.username}, role={self.role}, is_active={self.is_active}>"
