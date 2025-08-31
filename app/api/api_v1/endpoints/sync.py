from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models import (
    Product, Category, Customer, 
    Sale, SaleItem, Employee, Inventory
)
from app.models.user import User, UserRole
from app.core.sync_utils import sync_models, SyncResult

# Import schemas directly from their modules
from app.schemas.user import UserResponse as UserSchema
from app.schemas.product import ProductResponse as ProductSchema
from app.schemas.category import CategoryResponse as CategorySchema
from app.schemas.customer import CustomerResponse as CustomerSchema
from app.schemas.sale import SaleResponse as SaleSchema, SaleItemResponse as SaleItemSchema
from app.schemas.employee import EmployeeResponse as EmployeeSchema
from app.schemas.inventory import InventoryResponse as InventorySchema

router = APIRouter(prefix="/sync", tags=["sync"])

# Mapeamento de modelos para schemas Pydantic
MODEL_TO_SCHEMA = {
    "users": (User, UserSchema),
    "products": (Product, ProductSchema),
    "categories": (Category, CategorySchema),
    "customers": (Customer, CustomerSchema),
    "sales": (Sale, SaleSchema),
    "sale_items": (SaleItem, SaleItemSchema),
    "employees": (Employee, EmployeeSchema),
    "inventories": (Inventory, InventorySchema)
}

def get_model_and_schema(table_name: str):
    """Retorna o modelo e schema correspondentes ao nome da tabela"""
    model_schema = MODEL_TO_SCHEMA.get(table_name)
    if not model_schema:
        raise HTTPException(status_code=404, detail=f"Tabela {table_name} não encontrada")
    return model_schema

@router.get("/{table_name}", response_model=dict)
async def get_updates(
    table_name: str,
    last_sync: datetime = Query(..., description="Data da última sincronização"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna registros atualizados desde a última sincronização
    """
    model, _ = get_model_and_schema(table_name)
    
    # Busca registros atualizados desde a última sincronização
    updated_items = db.query(model).filter(
        model.last_updated > last_sync,
        model.is_active == True
    ).all()
    
    return {
        "server_updated": [item.to_dict() for item in updated_items],
        "synced_records": [],
        "conflicts": []
    }

@router.post("/{table_name}", response_model=dict)
async def sync_table(
    table_name: str,
    items: List[dict],
    last_sync: Optional[datetime] = Query(None, description="Data da última sincronização"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Sincroniza dados do cliente com o servidor
    """
    model, schema = get_model_and_schema(table_name)
    
    # Valida os itens recebidos
    try:
        validated_items = [schema(**item).dict() for item in items]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Dados inválidos: {str(e)}")
    
    # Executa a sincronização
    result = sync_models(db, model, validated_items, last_sync)
    
    return {
        "synced_records": result.synced_records,
        "conflicts": result.conflicts,
        "server_updated": result.server_updated
    }
