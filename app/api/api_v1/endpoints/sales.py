from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.sale import SaleResponse, CheckoutRequest, SaleStatus, PaymentMethod
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """Listar todas as vendas"""
    sales = db.query(Sale).filter(Sale.is_active == True).offset(skip).limit(limit).all()
    return sales

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """Obter venda por ID"""
    sale = db.query(Sale).filter(
        Sale.id == sale_id, 
        Sale.is_active == True
    ).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    return sale

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: CheckoutRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Criar nova venda"""
    # Gerar número de venda único
    sale_number = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Criar venda
    sale = Sale(
        sale_number=sale_number,
        status=SaleStatus.CONCLUIDA,
        subtotal=0,
        tax_amount=0,
        total_amount=0,
        payment_method=sale_data.payment_method,
        customer_id=sale_data.customer_id,
        notes=sale_data.notes
    )
    
    db.add(sale)
    db.commit()
    db.refresh(sale)
    
    return sale

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int, 
    sale_data: CheckoutRequest, 
    db: Session = Depends(get_db)
) -> Any:
    """Atualizar venda existente"""
    sale = db.query(Sale).filter(
        Sale.id == sale_id, 
        Sale.is_active == True
    ).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Atualizar campos
    sale.payment_method = sale_data.payment_method
    sale.customer_id = sale_data.customer_id
    sale.notes = sale_data.notes
    
    db.commit()
    db.refresh(sale)
    
    return sale

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    sale_id: int, 
    db: Session = Depends(get_db)
):
    """Deletar venda (soft delete)"""
    sale = db.query(Sale).filter(
        Sale.id == sale_id, 
        Sale.is_active == True
    ).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Soft delete
    sale.is_active = False
    db.commit()
