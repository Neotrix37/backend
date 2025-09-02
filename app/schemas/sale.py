from pydantic import BaseModel, Field
from typing import List, Optional
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
    quantity: float = Field(gt=0, default=1.0)  # Alterado para float para suportar decimais
    is_weight_sale: bool = False  # Indica se é venda por peso
    weight_in_kg: Optional[float] = Field(None, gt=0)  # Peso em kg para produtos vendidos por peso
    custom_price: Optional[float] = Field(None, gt=0)  # Preço personalizado para venda por peso

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 1.5,
                "is_weight_sale": True,
                "weight_in_kg": 0.5,
                "custom_price": 37.5
            }
        }

class CartItemResponse(CartItemCreate):
    """Resposta para itens do carrinho"""
    name: str = Field(..., alias="nome")
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
    product_name: str
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
        
    @classmethod
    def from_orm(cls, obj):
        # Garantir que temos o nome do produto disponível
        if hasattr(obj, 'product') and obj.product:
            # Usar setattr para evitar AttributeError
            setattr(obj, 'product_name', obj.product.nome)
        else:
            # Definir um valor padrão para product_name quando o produto não está disponível
            setattr(obj, 'product_name', "Produto não disponível")
        return super().from_orm(obj)

class SaleResponse(BaseModel):
    """Resposta da venda finalizada"""
    id: int
    sale_number: str
    status: SaleStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_method: str
    created_at: datetime
    items: List[SaleItemResponse] = []
    message: Optional[str] = None
    
    class Config:
        from_attributes = True
