from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .base import BaseResponse, BaseCreate

class MovementType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"
    RETURN = "return"
    LOSS = "loss"

class InventoryCreate(BaseCreate):
    movement_type: MovementType
    quantity: int
    previous_stock: int
    new_stock: int
    reference_id: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    product_id: int

class InventoryResponse(BaseResponse):
    movement_type: MovementType
    quantity: int
    previous_stock: int
    new_stock: int
    reference_id: Optional[str]
    reference_type: Optional[str]
    notes: Optional[str]
    product_id: int
