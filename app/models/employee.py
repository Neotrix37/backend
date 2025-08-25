from sqlalchemy import Column, String, Text, Boolean, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Employee(BaseModel):
    """Modelo para funcionários do sistema"""
    __tablename__ = "employees"
    
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    
    # Informações profissionais
    position = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)
    
    # Endereço
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    can_sell = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(name={self.name}, position={self.position})>"
