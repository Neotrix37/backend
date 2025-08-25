from datetime import date, timedelta
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from decimal import Decimal

from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse, SaleStatus, PaymentMethod, SaleItemCreate
from app.schemas.sale_item import SaleItemResponse
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.customer import Customer
from app.core.database import get_db
from app.core.pagination import Page, paginate

router = APIRouter()

@router.get("/", response_model=Page[SaleResponse])
async def get_sales(
    start_date: Optional[date] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data final (YYYY-MM-DD)"),
    status: Optional[SaleStatus] = Query(None, description="Status da venda"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Método de pagamento"),
    customer_id: Optional[int] = Query(None, description="ID do cliente"),
    page: int = Query(1, ge=1, description="Número da página", example=1),
    size: int = Query(20, ge=1, le=100, description="Itens por página", example=20),
    db: Session = Depends(get_db)
) -> Any:
    """
    Listar vendas com filtros e paginação
    
    - **start_date**: Filtrar a partir desta data (inclusive)
    - **end_date**: Filtrar até esta data (inclusive)
    - **status**: Filtrar por status da venda
    - **payment_method**: Filtrar por método de pagamento
    - **customer_id**: Filtrar por ID do cliente
    - **page**: Número da página (começando em 1)
    - **size**: Quantidade de itens por página (máx 100)
    """
    query = select(Sale).where(Sale.is_active == True)
    
    # Aplicar filtros
    if start_date:
        query = query.where(Sale.created_at >= start_date)
    if end_date:
        # Adiciona 1 dia para incluir o dia final
        query = query.where(Sale.created_at < end_date + timedelta(days=1))
    if status:
        query = query.where(Sale.status == status)
    if payment_method:
        query = query.where(Sale.payment_method == payment_method)
    if customer_id:
        query = query.where(Sale.customer_id == customer_id)
    
    # Ordenar por data de criação (mais recentes primeiro)
    query = query.order_by(Sale.created_at.desc())
    
    # Carregar relacionamentos necessários
    query = query.options(
        selectinload(Sale.items).selectinload(SaleItem.product),
        selectinload(Sale.customer)
    )
    
    # Aplicar paginação
    return paginate(db, query, page=page, size=size)

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(sale_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter venda por ID"""
    query = select(Sale).where(
        Sale.id == sale_id, 
        Sale.is_active == True
    ).options(
        selectinload(Sale.items).selectinload(SaleItem.product),
        selectinload(Sale.customer)
    )
    
    sale = db.execute(query).scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    return sale

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)) -> Any:
    """Criar nova venda com validação e cálculos"""
    # Iniciar transação
    with db.begin():
        # Verificar se o cliente existe
        customer = None
        if sale_data.customer_id:
            customer = db.get(Customer, sale_data.customer_id)
            if not customer or not customer.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cliente não encontrado ou inativo"
                )
        
        # Verificar itens e calcular totais
        subtotal = Decimal('0')
        items_to_add = []
        
        for item in sale_data.items:
            product = db.get(Product, item.product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Produto ID {item.product_id} não encontrado ou inativo"
                )
            
            if product.current_stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para o produto {product.name}. Disponível: {product.current_stock}"
                )
            
            # Calcular valores do item
            item_subtotal = item.unit_price * item.quantity
            item_discount = (item_subtotal * item.discount_percent) / 100
            item_total = item_subtotal - item_discount
            
            subtotal += item_total
            
            # Preparar item para adicionar
            items_to_add.append({
                "product_id": product.id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percent": item.discount_percent,
                "subtotal": item_total
            })
        
        # Calcular totais (exemplo: 10% de imposto)
        tax_rate = Decimal('0.1')
        tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'))
        total_amount = (subtotal + tax_amount).quantize(Decimal('0.01'))
        
        # Gerar número de venda
        last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
        new_number = f"V{1 if not last_sale else int(last_sale.sale_number[1:]) + 1:04d}"
        
        # Criar venda
        sale_dict = sale_data.model_dump(exclude={"items"})
        sale_dict.update({
            "sale_number": new_number,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "status": SaleStatus.COMPLETED,
            "payment_status": "paid"  # Ou outro status apropriado
        })
        
        new_sale = Sale(**sale_dict)
        db.add(new_sale)
        db.flush()  # Para obter o ID da venda
        
        # Adicionar itens
        for item_data in items_to_add:
            item = SaleItem(sale_id=new_sale.id, **item_data)
            db.add(item)
            
            # Atualizar estoque
            product = db.get(Product, item.product_id)
            product.current_stock -= item.quantity
        
        return new_sale

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: int, 
    sale_data: SaleUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """Atualizar venda existente"""
    sale = db.get(Sale, sale_id)
    if not sale or not sale.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Atualizar campos
    update_data = sale_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sale, field, value)
    
    db.commit()
    db.refresh(sale)
    return sale

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(sale_id: int, db: Session = Depends(get_db)) -> None:
    """Excluir venda (soft delete)"""
    sale = db.get(Sale, sale_id)
    if not sale or not sale.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Verificar se a venda pode ser excluída
    if sale.status == SaleStatus.COMPLETED:
        # Para vendas concluídas, marcar como cancelada em vez de excluir
        sale.status = SaleStatus.CANCELLED
        sale.is_active = False
    else:
        # Para outras situações, apenas marcar como inativa
        sale.is_active = False
    
    db.commit()
