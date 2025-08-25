from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from app.schemas.inventory import InventoryCreate, InventoryResponse
from app.models.inventory import Inventory
from app.models.product import Product
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[InventoryResponse])
async def get_inventory_movements(db: Session = Depends(get_db)) -> Any:
    """Listar todas as movimentações de inventário"""
    movements = db.query(Inventory).filter(Inventory.is_active == True).all()
    return movements

@router.get("/{movement_id}", response_model=InventoryResponse)
async def get_inventory_movement(movement_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter movimentação por ID"""
    movement = db.query(Inventory).filter(Inventory.id == movement_id, Inventory.is_active == True).first()
    
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação não encontrada"
        )
    
    return movement

@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_movement(movement_data: InventoryCreate, db: Session = Depends(get_db)) -> Any:
    """Criar nova movimentação de inventário"""
    # Verificar se o produto existe
    product = db.query(Product).filter(Product.id == movement_data.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Calcular estoque anterior e novo
    previous_stock = product.current_stock
    
    # Criar movimentação
    movement_dict = movement_data.model_dump()
    movement_dict['previous_stock'] = previous_stock
    
    if movement_data.movement_type == "purchase":
        movement_dict['new_stock'] = previous_stock + movement_data.quantity
        # Atualizar estoque do produto
        product.current_stock = movement_dict['new_stock']
    elif movement_data.movement_type == "sale":
        if previous_stock < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque insuficiente"
            )
        movement_dict['new_stock'] = previous_stock - movement_data.quantity
        # Atualizar estoque do produto
        product.current_stock = movement_dict['new_stock']
    elif movement_data.movement_type == "adjustment":
        movement_dict['new_stock'] = movement_data.quantity
        # Atualizar estoque do produto
        product.current_stock = movement_data.quantity
    
    new_movement = Inventory(**movement_dict)
    
    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    
    return new_movement
