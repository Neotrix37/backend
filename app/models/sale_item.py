from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import BaseModel

class SaleItem(BaseModel):
    """Modelo para itens individuais de cada venda"""
    __tablename__ = "sale_items"
    
    # Quantidade e preços
    quantity = Column(Numeric(10, 3), nullable=False, default=1)  # Alterado para Numeric para suportar decimais
    unit_price = Column(Numeric(10, 2), nullable=False, default=0)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0)
    total_price = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Campos para venda por peso
    is_weight_sale = Column(Boolean, default=False)
    weight_in_kg = Column(Numeric(10, 3), nullable=True)
    custom_price = Column(Numeric(10, 2), nullable=True)
    
    # Relacionamentos
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Relacionamentos
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    
    # Propriedade virtual para o nome do produto
    @hybrid_property
    def product_name(self):
        return self.product.nome if self.product else None
    
    @product_name.setter
    def product_name(self, value):
        # Esta é uma propriedade virtual, não armazenada no banco
        pass
    
    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, quantity={self.quantity}, total={self.total_price})>"
