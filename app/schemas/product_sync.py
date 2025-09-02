from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseCreate

class ProductSyncResponse(BaseCreate):
    """Schema específico para resposta de sincronização de produtos, sem validação de preço"""
    # Código e identificação
    codigo: str = Field(..., min_length=1, max_length=50, alias="sku")
    
    # Categoria
    category_id: Optional[int] = None
    
    # Informações básicas
    nome: str = Field(..., min_length=1, max_length=200, alias="name")
    descricao: Optional[str] = Field(None, alias="description")
    
    # Preços
    preco_compra: Decimal = Field(..., ge=0, alias="cost_price")
    preco_venda: Decimal = Field(..., ge=0, alias="sale_price")
    
    # Estoque
    estoque: int = Field(..., ge=0, alias="current_stock")
    estoque_minimo: int = Field(..., ge=0, alias="min_stock")
    
    # Configurações
    venda_por_peso: bool = False
    
    class Config:
        populate_by_name = True
        from_attributes = True