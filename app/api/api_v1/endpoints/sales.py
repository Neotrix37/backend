from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Any, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, or_
from sqlalchemy import and_

from app.schemas.sale import SaleCreate, SaleResponse, SaleUpdate
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.product import Product
from app.models.user import User, UserRole
from app.core.database import get_db
from app.core.security import (
    get_current_active_user,
    can_manage_sales,
    can_view_all_sales,
    can_close_register
)

router = APIRouter()

def format_sale_item(item: SaleItem) -> Dict[str, Any]:
    """Format a sale item to include the product name with the correct alias."""
    return {
        'id': item.id,
        'product_id': item.product_id,
        'product.nome': item.product.nome if item.product else 'Produto não encontrado',
        'quantity': float(item.quantity),
        'unit_price': float(item.unit_price),
        'total_price': float(item.total_price),
        'discount_percent': float(item.discount_percent),
        'created_at': item.created_at,
        'updated_at': item.updated_at
    }

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Criar uma nova venda.
    Apenas usuários com permissão de venda podem acessar.
    """
    # Verificar se o usuário tem permissão para vender
    if not (current_user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para realizar vendas"
        )
    
    # Criar a venda
    db_sale = Sale(
        **sale_data.dict(),
        user_id=current_user.id,
        sale_date=datetime.utcnow()
    )
    
    try:
        db.add(db_sale)
        db.commit()
        db.refresh(db_sale)
        return db_sale
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar venda: {str(e)}"
        )

@router.get("/", response_model=List[SaleResponse])
async def list_sales(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Listar vendas com filtros.
    - Admins e gerentes podem ver todas as vendas
    - Caixas só podem ver as próprias vendas
    - Viewers só podem ver vendas se tiverem permissão
    """
    # Primeiro, obter as vendas com os filtros aplicados
    query = db.query(Sale)
    
    # Aplicar filtro de data
    if start_date:
        query = query.filter(Sale.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Sale.created_at <= datetime.combine(end_date, datetime.max.time()))
    
    # Aplicar filtro de usuário
    if user_id:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores e gerentes podem filtrar por usuário"
            )
        query = query.filter(Sale.user_id == user_id)
    elif current_user.role == UserRole.CASHIER:
        query = query.filter(Sale.user_id == current_user.id)
    elif current_user.role == UserRole.VIEWER and not can_view_all_sales:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar vendas"
        )
    
    # Ordenar por data de criação (mais recente primeiro)
    query = query.order_by(Sale.created_at.desc())
    
    # Paginação
    offset = (page - 1) * limit
    sales = query.offset(offset).limit(limit).all()
    
    # Para cada venda, carregar os itens com os produtos
    result = []
    for sale in sales:
        # Carregar os itens da venda com os produtos
        items = db.query(SaleItem).join(Product).filter(SaleItem.sale_id == sale.id).all()
        
        # Criar dicionário com os dados da venda
        sale_dict = {
            'id': sale.id,
            'sale_number': sale.sale_number,
            'status': sale.status,
            'subtotal': float(sale.subtotal),
            'tax_amount': float(sale.tax_amount),
            'discount_amount': float(sale.discount_amount) if sale.discount_amount else 0.0,
            'total_amount': float(sale.total_amount),
            'payment_method': sale.payment_method,
            'created_at': sale.created_at,
            'items': [format_sale_item(item) for item in items]
        }
        result.append(sale_dict)
    
    return result

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obter detalhes de uma venda específica.
    Apenas o dono da venda, admin ou gerente podem acessar.
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Verificar permissão
    if (current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and 
        sale.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta venda"
        )
    
    return sale

@router.post("/{sale_id}/cancel", response_model=SaleResponse)
async def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cancelar uma venda.
    Apenas admin, gerente ou o dono da venda podem cancelar.
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Verificar permissão
    if (current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and 
        sale.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para cancelar esta venda"
        )
    
    # Marcar como cancelada
    sale.is_cancelled = True
    sale.cancelled_at = datetime.utcnow()
    sale.cancelled_by = current_user.id
    
    try:
        db.commit()
        db.refresh(sale)
        return sale
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao cancelar venda: {str(e)}"
        )

@router.post("/close-register", status_code=status.HTTP_200_OK)
async def close_register(
    db: Session = Depends(get_db),
    current_user: User = Depends(can_close_register)
) -> dict:
    """
    Fechar o caixa.
    Apenas caixas, gerentes e administradores podem acessar.
    """
    # Lógica para fechar o caixa
    # ...
    
    return {"status": "success", "message": "Caixa fechado com sucesso"}
