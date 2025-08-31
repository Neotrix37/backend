from pydantic import BaseModel, Field, validator
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
        json_encoders = {
            Decimal: lambda v: str(round(float(v), 2))
        }
    
    @validator('preco_compra', 'preco_venda', pre=True)
    def parse_decimal(cls, v):
        if isinstance(v, str):
            try:
                return Decimal(v.replace(',', '.'))
            except (ValueError, TypeError):
                pass
        return v
    
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
        json_encoders = {
            Decimal: lambda v: str(round(float(v), 2))
        }
    
    @validator('preco_compra', 'preco_venda', pre=True)
    def parse_decimal(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return Decimal(v.replace(',', '.'))
            except (ValueError, TypeError):
                pass
        return v
    
    @validator('preco_venda')
    def preco_venda_maior_que_custo(cls, v, values):
        if v is not None and 'preco_compra' in values and values['preco_compra'] is not None:
            if v <= values['preco_compra']:
                raise ValueError('Preço de venda deve ser maior que o preço de compra')
        return v

class ProductResponse(BaseResponse):
    # Código e identificação
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    codigo: str
    category_id: Optional[int] = None
    
    # Informações básicas
    nome: str
    descricao: Optional[str] = None
    
    # Preços (agora usando Decimal diretamente)
    preco_compra: Decimal = Field(..., ge=0)
    preco_venda: Decimal = Field(..., ge=0)
    
    # Estoque
    estoque: int
    estoque_minimo: int
    venda_por_peso: bool = False

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(round(float(v), 2))  # Converte Decimal para string com 2 casas decimais
        }
    
    @classmethod
    def from_orm(cls, obj):
        # Converte o objeto ORM para dicionário e garante que os decimais sejam tratados corretamente
        data = {
            'id': obj.id,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'is_active': obj.is_active,
            'codigo': obj.codigo,
            'category_id': obj.category_id,
            'nome': obj.nome,
            'descricao': obj.descricao,
            'preco_compra': obj.preco_compra,
            'preco_venda': obj.preco_venda,
            'estoque': obj.estoque,
            'estoque_minimo': obj.estoque_minimo,
            'venda_por_peso': obj.venda_por_peso
        }
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # Converte um dicionário para o modelo Pydantic
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
        
        return cls(**result)

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
