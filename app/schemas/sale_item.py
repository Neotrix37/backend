from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from .base import BaseResponse
from .product import ProductResponse

class SaleItemBase(BaseModel):
    """Base schema for sale items"""
    quantity: int = Field(..., gt=0, description="Quantidade vendida")
    unit_price: Decimal = Field(..., gt=0, decimal_places=2, description="Preço unitário no momento da venda")
    discount_percent: Decimal = Field(0, ge=0, le=100, decimal_places=2, description="Percentual de desconto aplicado")
    subtotal: Decimal = Field(..., gt=0, decimal_places=2, description="Subtotal (quantidade * preço - desconto)")
    notes: Optional[str] = Field(None, description="Observações sobre o item")

class SaleItemCreate(SaleItemBase):
    """Schema for creating a new sale item"""
    product_id: int = Field(..., description="ID do produto vendido")

class SaleItemUpdate(BaseModel):
    """Schema for updating an existing sale item"""
    quantity: Optional[int] = Field(None, gt=0, description="Nova quantidade")
    unit_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Novo preço unitário")
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2, description="Novo percentual de desconto")
    notes: Optional[str] = Field(None, description="Novas observações")

class SaleItemResponse(SaleItemBase, BaseResponse):
    """Schema for sale item responses"""
    id: int = Field(..., description="ID único do item")
    sale_id: int = Field(..., description="ID da venda relacionada")
    product_id: int = Field(..., description="ID do produto vendido")
    product: Optional[ProductResponse] = Field(None, description="Dados do produto")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")

    class Config:
        from_attributes = True
        json_encoders = {
            'decimal.Decimal': str  # Converte Decimal para string no JSON
        }
