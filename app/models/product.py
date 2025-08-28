from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Product(BaseModel):
    """Modelo para produtos do sistema"""
    __tablename__ = "products"
    
    # Código e identificação
    codigo = Column('sku', String(50), unique=True, index=True, nullable=False)
    
    # Relacionamentos
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # Informações básicas
    nome = Column('name', String(200), nullable=False, index=True)
    descricao = Column('description', Text, nullable=True)
    
    # Preços
    preco_compra = Column('cost_price', Numeric(10, 2), nullable=False, default=0)
    preco_venda = Column('sale_price', Numeric(10, 2), nullable=False, default=0)
    
    # Estoque
    estoque = Column('current_stock', Integer, nullable=False, default=0)
    estoque_minimo = Column('min_stock', Integer, nullable=False, default=0)
    
    # Configurações
    venda_por_peso = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos adicionais
    sale_items = relationship("SaleItem", back_populates="product", 
                            passive_deletes='all',  # Não tenta excluir os itens
                            foreign_keys='SaleItem.product_id')
    inventory_movements = relationship("Inventory", back_populates="product")
    
    def __repr__(self):
        return f"<Product(nome={self.nome}, codigo={self.codigo}>"
