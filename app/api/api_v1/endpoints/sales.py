import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Any, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.schemas.sale import SaleResponse, CheckoutRequest, SaleStatus
from app.models.sale import Sale
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.sale_item import SaleItem

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all sales with their items and product details"""
    try:
        # Carrega as vendas com seus itens e produtos relacionados
        sales = db.query(Sale)\
            .options(
                joinedload(Sale.items)\
                .joinedload(SaleItem.product)\
            )\
            .filter(Sale.is_active == True)\
            .order_by(Sale.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
            
        # Prepara a resposta incluindo os itens com detalhes do produto
        result = []
        for sale in sales:
            sale_dict = {
                "id": sale.id,
                "sale_number": sale.sale_number,
                "status": sale.status,
                "subtotal": float(sale.subtotal) if sale.subtotal else 0.0,
                "tax_amount": float(sale.tax_amount) if sale.tax_amount else 0.0,
                "discount_amount": float(sale.discount_amount) if sale.discount_amount else 0.0,
                "total_amount": float(sale.total_amount) if sale.total_amount else 0.0,
                "payment_method": sale.payment_method,
                "created_at": sale.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "product_name": item.product.nome if item.product else "Produto não encontrado",
                        "quantity": float(item.quantity) if item.quantity else 0.0,
                        "unit_price": float(item.unit_price) if item.unit_price else 0.0,
                        "total_price": float(item.total_price) if item.total_price else 0.0,
                        "is_weight_sale": bool(getattr(item, 'is_weight_sale', False)),
                        "weight_in_kg": float(getattr(item, 'weight_in_kg', 0)) if getattr(item, 'weight_in_kg', None) else None,
                        "custom_price": float(getattr(item, 'custom_price', 0)) if getattr(item, 'custom_price', None) else None,
                        "created_at": item.created_at
                    } for item in sale.items
                ]
            }
            result.append(sale_dict)
            
        return result
    except Exception as e:
        logger.error(f"Error fetching sales: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching sales."
        )

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get sale by ID with items and product details"""
    try:
        # Carrega a venda com seus itens e produtos relacionados
        sale = db.query(Sale)\
            .options(
                joinedload(Sale.items)\
                .joinedload(SaleItem.product)\
            )\
            .filter(Sale.id == sale_id, Sale.is_active == True)\
            .first()
            
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        
        # Prepara a resposta incluindo os itens com detalhes do produto
        result = {
            "id": sale.id,
            "sale_number": sale.sale_number,
            "status": sale.status,
            "subtotal": float(sale.subtotal) if sale.subtotal else 0.0,
            "tax_amount": float(sale.tax_amount) if sale.tax_amount else 0.0,
            "discount_amount": float(sale.discount_amount) if sale.discount_amount else 0.0,
            "total_amount": float(sale.total_amount) if sale.total_amount else 0.0,
            "payment_method": sale.payment_method,
            "created_at": sale.created_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": item.product.nome if item.product else "Produto não encontrado",
                    "quantity": float(item.quantity) if item.quantity else 0.0,
                    "unit_price": float(item.unit_price) if item.unit_price else 0.0,
                    "total_price": float(item.total_price) if item.total_price else 0.0,
                    "is_weight_sale": bool(getattr(item, 'is_weight_sale', False)),
                    "weight_in_kg": float(getattr(item, 'weight_in_kg', 0)) if getattr(item, 'weight_in_kg', None) else None,
                    "custom_price": float(getattr(item, 'custom_price', 0)) if getattr(item, 'custom_price', None) else None,
                    "created_at": item.created_at
                } for item in sale.items
            ]
        }
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sale {sale_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the sale."
        )

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create a new sale"""
    try:
        sale_number = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
        sale = Sale(
            sale_number=sale_number,
            status=SaleStatus.CONCLUIDA,
            subtotal=0,  # These should be calculated based on cart items
            tax_amount=0,
            total_amount=0,
            payment_method=sale_data.payment_method,
            customer_id=sale_data.customer_id,
            notes=sale_data.notes,
            created_by=current_user.id
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale
    except Exception as e:
        logger.error(f"Error creating sale: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the sale."
        )

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int,
    sale_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update an existing sale"""
    try:
        sale = db.query(Sale).filter(Sale.id == sale_id, Sale.is_active == True).first()
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        
        # Update fields
        sale.payment_method = sale_data.payment_method
        sale.customer_id = sale_data.customer_id
        sale.notes = sale_data.notes
        
        db.commit()
        db.refresh(sale)
        return sale
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sale {sale_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the sale."
        )

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sale (soft delete)"""
    try:
        sale = db.query(Sale).filter(Sale.id == sale_id, Sale.is_active == True).first()
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        
        sale.is_active = False
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sale {sale_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the sale."
        )
