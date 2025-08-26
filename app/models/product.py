from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Product(BaseModel):
    """Modelo para produtos do sistema"""
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    barcode = Column(String(50), unique=True, index=True, nullable=True)
    
    # Preços
    cost_price = Column(Numeric(10, 2), nullable=False, default=0)
    sale_price = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Estoque
    current_stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=0)
    
    # Categoria
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    venda_por_peso = Column(Boolean, default=False, nullable=False)  # Se é vendido por peso/kg
    
    # Relacionamentos
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    inventory_movements = relationship("Inventory", back_populates="product")
    
    def __repr__(self):
        return f"<Product(name={self.name}, sku={self.sku}>"
