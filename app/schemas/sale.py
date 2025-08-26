from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CartItemCreate(BaseModel):
    """Esquema para adicionar item ao carrinho"""
    product_id: int
    quantity: int = Field(gt=0, default=1)

class CartItemResponse(CartItemCreate):
    """Resposta para itens do carrinho"""
    name: str
    unit_price: float
    total_price: float

class CartResponse(BaseModel):
    """Resposta com o carrinho de compras"""
    items: List[CartItemResponse] = []
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0

class PaymentMethod(str, Enum):
    """Métodos de pagamento disponíveis"""
    DINHEIRO = "dinheiro"
    CREDITO = "credito"
    DEBITO = "debito"
    PIX = "pix"

class CheckoutRequest(BaseModel):
    """Dados para finalizar a venda"""
    payment_method: PaymentMethod
    customer_id: Optional[int] = None
    notes: Optional[str] = None

class SaleResponse(BaseModel):
    """Resposta da venda finalizada"""
    id: int
    sale_number: str
    total_amount: float
    payment_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True
