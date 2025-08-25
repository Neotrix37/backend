from sqlalchemy import Column, String, Text, Boolean, Date
from sqlalchemy.orm import relationship
from .base import BaseModel

class Customer(BaseModel):
    """Modelo para clientes do sistema"""
    __tablename__ = "customers"
    
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    cpf_cnpj = Column(String(18), unique=True, index=True, nullable=True)
    
    # Endereço
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Informações adicionais
    birth_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_vip = Column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    sales = relationship("Sale", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(name={self.name}, cpf_cnpj={self.cpf_cnpj})>"
