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
            "nome": product.nome,
            "quantity": item.quantity,
            "unit_price": float(product.preco_venda),
            "total_price": float(product.preco_venda * item.quantity)
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
    import logging
    logger = logging.getLogger(__name__)
    
    cart = get_or_create_cart(session_id)
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O carrinho está vazio"
        )
    
    logger.info(f"Iniciando checkout para carrinho: {cart}")
    
    try:
        # Cálculo dos totais (sem IVA)
        cart_data = _calculate_cart_totals(cart)
        logger.info(f"Totais calculados: {cart_data.__dict__}")
        
        # Cria a venda
        sale = Sale(
            sale_number=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status=SaleStatus.CONCLUIDA,
            subtotal=float(cart_data.subtotal),
            tax_amount=0.0,  # Sem IVA
            total_amount=float(cart_data.subtotal),  # Total igual ao subtotal
            payment_method=PaymentMethod(checkout_data.payment_method),
            customer_id=checkout_data.customer_id,
            notes=checkout_data.notes
        )
        
        db.add(sale)
        db.flush()  # Gera o ID da venda sem fazer commit
        logger.info(f"Venda criada com ID: {sale.id}")
        
        # Adiciona os itens da venda e atualiza o estoque
        for item in cart_data.items:
            logger.info(f"Processando item: {item}")
            
            # Busca o produto para atualizar o estoque
            product = db.query(Product).filter(
                Product.id == item["product_id"],
                Product.is_active == True
            ).with_for_update().first()  # Bloqueia o registro para atualização
            
            if not product:
                db.rollback()
                logger.error(f"Produto com ID {item['product_id']} não encontrado")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Produto com ID {item['product_id']} não encontrado"
                )
            
            logger.info(f"Produto encontrado: {product.nome}, Estoque atual: {product.estoque}")
            
            # Verifica se há estoque suficiente
            if product.estoque < item["quantity"]:
                db.rollback()
                logger.error(f"Estoque insuficiente para o produto {product.nome}. Estoque atual: {product.estoque}, Quantidade solicitada: {item['quantity']}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para o produto {product.nome}"
                )
            
            # Atualiza o estoque
            novo_estoque = product.estoque - item["quantity"]
            logger.info(f"Atualizando estoque do produto {product.id} de {product.estoque} para {novo_estoque}")
            product.estoque = novo_estoque
            db.add(product)
            
            # Cria o item da venda
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=float(item["unit_price"]),
                total_price=float(item["total_price"])
            )
            db.add(sale_item)
            logger.info(f"Item de venda criado: {sale_item}")
        
        # Confirma a transação
        db.commit()
        logger.info("Transação confirmada com sucesso")
        
        # Atualiza o objeto de venda para garantir que todos os dados estejam disponíveis
        db.refresh(sale)
        
        # Limpa o carrinho após a finalização
        cart_store.pop(session_id, None)
        logger.info("Carrinho limpo após finalização")
        
        return sale
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao processar a venda: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a venda: {str(e)}"
        )

@router.delete("/cart/items/{product_id}", response_model=dict)
async def remove_item_from_cart(
    product_id: int,
    session_id: str = "default",
) -> dict:
    """Remove um item específico do carrinho"""
    if session_id not in cart_store or not cart_store[session_id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrinho não encontrado ou vazio"
        )
    
    cart = cart_store[session_id]
    initial_count = len(cart)
    cart[:] = [item for item in cart if item["product_id"] != product_id]
    
    if len(cart) == initial_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {product_id} não encontrado no carrinho"
        )
    
    return {"status": "success", "message": f"Produto {product_id} removido do carrinho"}

@router.delete("/cart", response_model=dict)
async def clear_cart(
    session_id: str = "default",
) -> dict:
    """Remove todos os itens do carrinho"""
    if session_id in cart_store:
        cart_store[session_id] = []  # Mantém a estrutura mas limpa os itens
        return {"status": "success", "message": "Carrinho limpo com sucesso"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Carrinho não encontrado"
    )

def _calculate_cart_totals(cart: List[Dict[str, Any]]) -> Any:
    """Calcula os totais do carrinho (sem IVA)"""
    class CartTotals:
        def __init__(self, items=None, subtotal=0, tax_amount=0, total=0):
            self.items = items or []
            self.subtotal = subtotal
            self.tax_amount = tax_amount
            self.total = total
    
    if not cart:
        return CartTotals()
    
    items = []
    subtotal = 0
    
    for item in cart:
        item_total = float(item["unit_price"]) * int(item["quantity"])
        items.append({
            "product_id": item["product_id"],
            "nome": item["nome"],
            "quantity": int(item["quantity"]),
            "unit_price": float(item["unit_price"]),
            "total_price": item_total
        })
        subtotal += item_total
    
    # Sem IVA
    tax_amount = 0
    total = subtotal
    
    return CartTotals(items, subtotal, tax_amount, total)
