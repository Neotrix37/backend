from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel

class MovementType(str, enum.Enum):
    PURCHASE = "purchase"      # Compra
    SALE = "sale"             # Venda
    ADJUSTMENT = "adjustment"  # Ajuste manual
    TRANSFER = "transfer"      # Transferência entre locais
    RETURN = "return"          # Devolução
    LOSS = "loss"             # Perda/Quebra

class Inventory(BaseModel):
    """Modelo para controle de movimentações de estoque"""
    __tablename__ = "inventory_movements"
    
    # Tipo de movimentação
    movement_type = Column(Enum(MovementType), nullable=False)
    
    # Quantidades
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Referências
    reference_id = Column(String(100), nullable=True)  # ID da venda, compra, etc.
    reference_type = Column(String(50), nullable=True)  # Tipo da referência
    
    # Observações
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Relacionamentos
    product = relationship("Product", back_populates="inventory_movements")
    
    def __repr__(self):
        return f"<Inventory(type={self.movement_type}, quantity={self.quantity}, product_id={self.product_id})>"
