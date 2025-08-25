from sqlalchemy import Column, String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class SaleItem(BaseModel):
    """Modelo para itens individuais de cada venda"""
    __tablename__ = "sale_items"
    
    # Quantidade e preços
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False, default=0)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0)
    total_price = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Relacionamentos
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Relacionamentos
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    
    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, quantity={self.quantity}, total={self.total_price})>"
