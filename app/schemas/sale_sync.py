from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .base import BaseCreate
from .sale import SaleStatus, PaymentMethod, CartItemCreate

class SaleItemSyncResponse(BaseModel):
    """Resposta para itens da venda na sincronização"""
    product_id: int
    quantity: float
    unit_price: float
    total_price: float
    is_weight_sale: bool = Field(False)
    weight_in_kg: Optional[float] = None
    custom_price: Optional[float] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class SaleSyncResponse(BaseCreate):
    """Schema específico para resposta de sincronização de vendas"""
    sale_number: str
    status: SaleStatus = SaleStatus.PENDENTE
    subtotal: float
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total_amount: float
    payment_method: PaymentMethod
    customer_id: Optional[int] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    items: List[SaleItemSyncResponse] = []
    
    class Config:
        populate_by_name = True
        from_attributes = True