from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
from .base import BaseResponse, BaseCreate, BaseUpdate

class ProductCreate(BaseCreate):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    
    # Preços
    cost_price: Decimal = Field(..., ge=0)
    sale_price: Decimal = Field(..., ge=0)
    wholesale_price: Optional[Decimal] = Field(None, ge=0)
    
    # Estoque
    current_stock: int = Field(..., ge=0)
    min_stock: int = Field(..., ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    
    # Categoria
    category_id: Optional[int] = None
    
    # Status
    is_service: bool = False
    venda_por_peso: bool = False  # Se é vendido por peso/kg
    
    @validator('sale_price')
    def sale_price_must_be_greater_than_cost(cls, v, values):
        if 'cost_price' in values and v <= values['cost_price']:
            raise ValueError('Preço de venda deve ser maior que o preço de custo')
        return v
    
    @validator('max_stock')
    def max_stock_must_be_greater_than_min(cls, v, values):
        if v is not None and 'min_stock' in values and v <= values['min_stock']:
            raise ValueError('Estoque máximo deve ser maior que o estoque mínimo')
        return v

class ProductUpdate(BaseUpdate):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    
    # Preços
    cost_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    wholesale_price: Optional[Decimal] = Field(None, ge=0)
    
    # Estoque
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    
    # Categoria
    category_id: Optional[int] = None
    
    # Status
    is_service: Optional[bool] = None
    is_active: Optional[bool] = None
    venda_por_peso: Optional[bool] = None

class ProductResponse(BaseResponse):
    name: str
    description: Optional[str]
    sku: str
    barcode: Optional[str]
    cost_price: Decimal
    sale_price: Decimal
    wholesale_price: Optional[Decimal]
    current_stock: int
    min_stock: int
    max_stock: Optional[int]
    category_id: Optional[int]
    is_service: bool
    venda_por_peso: bool
