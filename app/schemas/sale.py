from pydantic import BaseModel, Field, validator
from typing import Optional, List, ForwardRef
from decimal import Decimal
from enum import Enum
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate
from .sale_item import SaleItemResponse

# Forward reference to avoid circular imports
CustomerResponse = ForwardRef('CustomerResponse')

class SaleStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"

class SaleItemCreate(BaseModel):
    product_id: int = Field(..., description="ID do produto")
    quantity: int = Field(..., gt=0, description="Quantidade")
    unit_price: Decimal = Field(..., gt=0, decimal_places=2, description="Preço unitário")
    discount_percent: Decimal = Field(0, ge=0, le=100, decimal_places=2, description="Percentual de desconto")

class SaleCreate(BaseCreate):
    customer_id: Optional[int] = Field(None, description="ID do cliente")
    employee_id: Optional[int] = Field(None, description="ID do funcionário")
    payment_method: Optional[PaymentMethod] = Field(None, description="Método de pagamento")
    notes: Optional[str] = Field(None, description="Observações da venda")
    is_delivery: bool = Field(False, description="Se a venda é para entrega")
    delivery_address: Optional[str] = Field(None, description="Endereço de entrega")
    items: List[SaleItemCreate] = Field(..., min_items=1, description="Itens da venda")

class SaleUpdate(BaseUpdate):
    status: Optional[SaleStatus] = Field(None, description="Novo status da venda")
    payment_status: Optional[str] = Field(None, description="Status do pagamento")
    notes: Optional[str] = Field(None, description="Observações adicionais")

class SaleResponse(BaseResponse):
    sale_number: str = Field(..., description="Número único da venda")
    status: SaleStatus = Field(..., description="Status atual da venda")
    subtotal: Decimal = Field(..., description="Soma dos itens sem descontos")
    tax_amount: Decimal = Field(..., description="Valor total de impostos")
    discount_amount: Decimal = Field(..., description="Valor total de descontos")
    total_amount: Decimal = Field(..., description="Valor total da venda")
    payment_method: Optional[PaymentMethod] = Field(None, description="Método de pagamento")
    payment_status: Optional[str] = Field(None, description="Status do pagamento")
    customer_id: Optional[int] = Field(None, description="ID do cliente")
    customer: Optional[CustomerResponse] = Field(None, description="Dados do cliente")
    employee_id: Optional[int] = Field(None, description="ID do funcionário")
    notes: Optional[str] = Field(None, description="Observações da venda")
    is_delivery: bool = Field(False, description="Se a venda é para entrega")
    delivery_address: Optional[str] = Field(None, description="Endereço de entrega")
    items: List[SaleItemResponse] = Field(default_factory=list, description="Itens da venda")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")

    class Config:
        from_attributes = True
        json_encoders = {
            'decimal.Decimal': str  # Converte Decimal para string no JSON
        }

# Atualizar referências circulares
from .customer import CustomerResponse  # noqa
SaleResponse.update_forward_refs()
