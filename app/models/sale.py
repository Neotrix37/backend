from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class SaleStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"

class Sale(BaseModel):
    """Modelo para vendas do sistema"""
    __tablename__ = "sales"
    
    # Informações da venda
    sale_number = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(Enum(SaleStatus), default=SaleStatus.PENDING, nullable=False)
    
    # Valores
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Pagamento
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_status = Column(String(50), nullable=True)
    
    # Relacionamentos
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Campos adicionais
    notes = Column(Text, nullable=True)
    is_delivery = Column(Boolean, default=False, nullable=False)
    delivery_address = Column(Text, nullable=True)
    
    # Relacionamentos
    customer = relationship("Customer", back_populates="sales")
    employee = relationship("Employee", back_populates="sales")
    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale(number={self.sale_number}, total={self.total_amount})>"
