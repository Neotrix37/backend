from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from enum import Enum
from .base import BaseResponse, BaseCreate, BaseUpdate

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
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(0, ge=0, le=100)

class SaleCreate(BaseCreate):
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    is_delivery: bool = False
    delivery_address: Optional[str] = None
    items: List[SaleItemCreate]

class SaleUpdate(BaseUpdate):
    status: Optional[SaleStatus] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None

class SaleResponse(BaseResponse):
    sale_number: str
    status: SaleStatus
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_method: Optional[PaymentMethod]
    payment_status: Optional[str]
    customer_id: Optional[int]
    employee_id: Optional[int]
    user_id: Optional[int]
    notes: Optional[str]
    is_delivery: bool
    delivery_address: Optional[str]
