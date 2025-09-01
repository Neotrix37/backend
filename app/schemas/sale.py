from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SaleStatus(str, Enum):
    """Status possíveis de uma venda"""
    PENDENTE = "pendente"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    REEMBOLSADA = "reembolsada"

class PaymentMethod(str, Enum):
    """Métodos de pagamento disponíveis"""
    DINHEIRO = "DINHEIRO"
    MPESA = "MPESA"
    EMOLA = "EMOLA"
    CARTAO_POS = "CARTAO_POS"
    TRANSFERENCIA = "TRANSFERENCIA"
    MILLENNIUM = "MILLENNIUM"
    BCI = "BCI"
    STANDARD_BANK = "STANDARD_BANK"
    ABSA_BANK = "ABSA_BANK"
    LETSHEGO = "LETSHEGO"
    MYBUCKS = "MYBUCKS"

class CartItemCreate(BaseModel):
    """Esquema para adicionar item ao carrinho"""
    product_id: int
    quantity: float = Field(1, gt=0)  # Alterado para float para suportar decimais
    is_weight_sale: bool = False  # Indica se é venda por peso
    weight_in_kg: Optional[float] = Field(None, gt=0)  # Peso em kg para produtos vendidos por peso
    custom_price: Optional[float] = Field(None, gt=0)  # Preço personalizado para venda por peso
    update_quantity: bool = False  # Flag to indicate if we should update the quantity instead of adding to it

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 1.5,
                "is_weight_sale": True,
                "weight_in_kg": 0.5,
                "custom_price": 37.5,
                "update_quantity": False
            }
        }

class CartItemResponse(CartItemCreate):
    """Resposta para itens do carrinho"""
    name: str = Field(..., alias="nome")
    sku: Optional[str] = None  # Add SKU field
    unit_price: float
    total_price: float
    is_weight_sale: bool = False  # Adicionado para o frontend saber se é venda por peso
    weight_in_kg: Optional[float] = None
    custom_price: Optional[float] = None

class CartResponse(BaseModel):
    """Resposta com o carrinho de compras"""
    items: List[CartItemResponse] = []
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total: float = 0.0

class CheckoutRequest(BaseModel):
    """Dados para finalizar a venda"""
    payment_method: PaymentMethod
    customer_id: Optional[int] = None
    notes: Optional[str] = None

class SaleItemResponse(BaseModel):
    """Resposta para itens da venda"""
    id: int
    product_id: int
    product: Dict[str, Any] = Field(..., description="Informações completas do produto")
    quantity: float
    unit_price: float
    total_price: float
    is_weight_sale: bool = False
    weight_in_kg: Optional[float] = None
    custom_price: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SaleResponse(BaseModel):
    """Resposta da venda finalizada"""
    id: int
    sale_number: str
    status: SaleStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_method: PaymentMethod
    created_at: datetime
    items: List[SaleItemResponse] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            PaymentMethod: lambda v: v.value,
            SaleStatus: lambda v: v.value
        }

class SaleCreate(BaseModel):
    """Schema para criar uma nova venda"""
    customer_id: Optional[int] = None
    payment_method: PaymentMethod
    notes: Optional[str] = None
    items: List[CartItemCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "payment_method": "DINHEIRO",
                "notes": "Cliente solicitou nota fiscal",
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2,
                        "is_weight_sale": False,
                        "update_quantity": False
                    },
                    {
                        "product_id": 2,
                        "quantity": 1.5,
                        "is_weight_sale": True,
                        "weight_in_kg": 1.5,
                        "custom_price": 75.50,
                        "update_quantity": False
                    }
                ]
            }
        }

class SaleUpdate(BaseModel):
    """Schema para atualizar uma venda existente"""
    status: Optional[SaleStatus] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    customer_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "concluida",
                "payment_method": "MPESA",
                "notes": "Pagamento confirmado via M-Pesa",
                "customer_id": 1
            }
        }
