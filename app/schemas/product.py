from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, Dict, Any, Union
from decimal import Decimal
from datetime import datetime
from .base import BaseResponse, BaseCreate, BaseUpdate

class ProductCreate(BaseCreate):
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
    
    @validator('preco_venda')
    def preco_venda_maior_que_custo(cls, v, values):
        if 'preco_compra' in values and v <= values['preco_compra']:
            raise ValueError('Preço de venda deve ser maior que o preço de compra')
        return v

class ProductUpdate(BaseUpdate):
    # Código e identificação
    codigo: Optional[str] = Field(None, min_length=1, max_length=50, alias="sku")
    
    # Categoria
    category_id: Optional[int] = None
    
    # Informações básicas
    nome: Optional[str] = Field(None, min_length=1, max_length=200, alias="name")
    descricao: Optional[str] = Field(None, alias="description")
    
    # Preços
    preco_compra: Optional[Decimal] = Field(None, ge=0, alias="cost_price")
    preco_venda: Optional[Decimal] = Field(None, ge=0, alias="sale_price")
    
    # Estoque
    estoque: Optional[int] = Field(None, ge=0, alias="current_stock")
    estoque_minimo: Optional[int] = Field(None, ge=0, alias="min_stock")
    
    # Configurações
    venda_por_peso: Optional[bool] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True

class ProductResponse(BaseResponse):
    # Identificação
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    # Dados do produto
    codigo: str
    category_id: Optional[int] = None
    nome: str
    descricao: Optional[str] = None
    
    # Preços
    preco_compra: str
    preco_venda: str
    
    # Estoque
    estoque: int
    estoque_minimo: int
    
    # Configurações
    venda_por_peso: bool = False

    @model_validator(mode='before')
    @classmethod
    def prepare_response(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            # Se for um objeto SQLAlchemy, converte para dicionário
            data_dict = {
                'id': getattr(data, 'id', 0),
                'created_at': getattr(data, 'created_at'),
                'updated_at': getattr(data, 'updated_at'),
                'is_active': getattr(data, 'is_active', True),
                'codigo': getattr(data, 'codigo', getattr(data, 'sku', '')),
                'category_id': getattr(data, 'category_id', None),
                'nome': getattr(data, 'nome', getattr(data, 'name', '')),
                'descricao': getattr(data, 'descricao', getattr(data, 'description', None)),
                'preco_compra': format_decimal(getattr(data, 'preco_compra', getattr(data, 'cost_price', Decimal('0')))),
                'preco_venda': format_decimal(getattr(data, 'preco_venda', getattr(data, 'sale_price', Decimal('0')))),
                'estoque': getattr(data, 'estoque', getattr(data, 'current_stock', 0)),
                'estoque_minimo': getattr(data, 'estoque_minimo', getattr(data, 'min_stock', 0)),
                'venda_por_peso': getattr(data, 'venda_por_peso', False)
            }
            return data_dict
        
        # Se já for um dicionário, apenas garante que todos os campos estão presentes
        field_mapping = {
            'sku': 'codigo',
            'name': 'nome',
            'description': 'descricao',
            'cost_price': 'preco_compra',
            'sale_price': 'preco_venda',
            'current_stock': 'estoque',
            'min_stock': 'estoque_minimo'
        }
        
        # Copia os valores dos campos antigos para os novos, se necessário
        result = {}
        for old_field, new_field in field_mapping.items():
            if old_field in data and new_field not in data:
                result[new_field] = data[old_field]
            elif new_field in data:
                result[new_field] = data[new_field]
        
        # Adiciona os campos que não são mapeados
        for field in ['id', 'created_at', 'updated_at', 'is_active', 'category_id', 'venda_por_peso']:
            if field in data:
                result[field] = data[field]
        
        # Formata os preços
        for price_field in ['preco_compra', 'preco_venda']:
            if price_field in result and isinstance(result[price_field], (Decimal, float, int)):
                result[price_field] = format_decimal(result[price_field])
                
        return result

    class Config:
        from_attributes = True
        populate_by_name = True

def format_decimal(value) -> str:
    """Formata um valor decimal para string com 2 casas decimais"""
    if value is None:
        return "0.00"
    if isinstance(value, str):
        try:
            value = Decimal(value)
        except:
            return "0.00"
    return f"{float(value):.2f}"
