from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Category(BaseModel):
    """Modelo para categorias de produtos"""
    __tablename__ = "categories"
    
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Código hexadecimal da cor
    
    # Relacionamentos
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name={self.name})>"
