from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.schemas.sale import CartItemCreate, CartResponse, CheckoutRequest, SaleResponse, PaymentMethod

router = APIRouter(tags=["cart"])

# Armazenamento temporário do carrinho (em produção, use Redis ou banco de dados)
cart_store: Dict[str, List[Dict[str, Any]]] = {}

def get_or_create_cart(session_id: str) -> List[Dict[str, Any]]:
    """Obtém ou cria um carrinho para a sessão"""
    if session_id not in cart_store:
        cart_store[session_id] = []
    return cart_store[session_id]

@router.post("/add", response_model=CartResponse)
async def add_to_cart(
    item: CartItemCreate,
    session_id: str = "default",  # Em produção, use um ID de sessão real
    db: Session = Depends(get_db)
) -> Any:
    """Adiciona um item ao carrinho"""
    # Verifica se o produto existe
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Obtém o carrinho da sessão
    cart = get_or_create_cart(session_id)
    
    # Verifica se o item já está no carrinho
    item_index = next((i for i, x in enumerate(cart) if x["product_id"] == item.product_id), None)
    
    if item_index is not None:
        # Atualiza a quantidade se o item já existir
        cart[item_index]["quantity"] += item.quantity
    else:
        # Adiciona novo item ao carrinho
        cart.append({
            "product_id": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "unit_price": float(product.price),
            "total_price": float(product.price * item.quantity)
        })
    
    return _calculate_cart_totals(cart)

@router.get("", response_model=CartResponse)
async def view_cart(
    session_id: str = "default"
) -> Any:
    """Visualiza o carrinho atual"""
    cart = get_or_create_cart(session_id)
    return _calculate_cart_totals(cart)

@router.post("/checkout", response_model=SaleResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    session_id: str = "default",
    db: Session = Depends(get_db)
) -> Any:
    """Finaliza a compra e cria a venda"""
    cart = get_or_create_cart(session_id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O carrinho está vazio"
        )
    
    # Cálculo dos totais
    cart_data = _calculate_cart_totals(cart)
    
    # Cria a venda
    sale = Sale(
        sale_number=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status=SaleStatus.CONCLUIDA,
        subtotal=cart_data.subtotal,
        tax_amount=cart_data.tax_amount,
        total_amount=cart_data.total,
        payment_method=PaymentMethod(checkout_data.payment_method),
        customer_id=checkout_data.customer_id,
        notes=checkout_data.notes
    )
    
    db.add(sale)
    db.commit()
    db.refresh(sale)
    
    # Adiciona os itens da venda
    for item in cart_data.items:
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(sale_item)
    
    db.commit()
    
    # Limpa o carrinho após a finalização
    cart_store.pop(session_id, None)
    
    return sale

def _calculate_cart_totals(cart: List[Dict[str, Any]]) -> CartResponse:
    """Calcula os totais do carrinho"""
    items = []
    subtotal = 0.0
    
    # Calcula subtotal e itens
    for item in cart:
        item_total = item["unit_price"] * item["quantity"]
        item["total_price"] = item_total
        subtotal += item_total
        
        items.append({
            "product_id": item["product_id"],
            "name": item["name"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total_price": item_total
        })
    
    # Cálculo de impostos (exemplo: 10%)
    tax_rate = 0.10
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    return CartResponse(
        items=items,
        subtotal=round(subtotal, 2),
        tax_amount=round(tax_amount, 2),
        total=round(total, 2)
    )
