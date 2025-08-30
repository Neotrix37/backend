from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.schemas.sale import CartItemCreate, CartResponse, CheckoutRequest, SaleResponse, PaymentMethod, CartItemResponse
from app.models.user import User
from app.core.security import get_current_active_user  # Atualizado para o caminho correto

router = APIRouter(tags=["cart"])

# Armazenamento temporário do carrinho (em produção, use Redis ou banco de dados)
cart_store: Dict[str, Dict[str, Any]] = {}

def get_or_create_cart(session_id: str, user_id: int) -> Dict[str, Any]:
    """Obtém ou cria um carrinho para a sessão"""
    if session_id not in cart_store:
        cart_store[session_id] = {
            "items": [],
            "created_at": datetime.utcnow(),
            "user_id": user_id
        }
    return cart_store[session_id]

@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adiciona um item ao carrinho"""
    # Obter o produto
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado ou inativo")
    
    # Verificar se é venda por peso
    if product.venda_por_peso:
        if not item.is_weight_sale or item.weight_in_kg is None or item.custom_price is None:
            raise HTTPException(
                status_code=400,
                detail="Para produtos vendidos por peso, é necessário informar o peso e o preço personalizado"
            )
        # Usar o peso informado para a quantidade
        quantity = item.weight_in_kg
        unit_price = item.custom_price / item.weight_in_kg if item.weight_in_kg > 0 else 0
        total_price = item.custom_price
    else:
        # Venda normal por unidade
        quantity = item.quantity
        unit_price = float(product.preco_venda)
        total_price = unit_price * quantity
    
    # Verificar estoque (se aplicável)
    if not product.venda_por_peso and product.estoque < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Estoque insuficiente. Disponível: {product.estoque}"
        )
    
    # Inicializar carrinho se não existir
    cart = get_or_create_cart(session_id, current_user.id)
    
    # Verificar se o produto já está no carrinho
    item_index = next(
        (i for i, x in enumerate(cart["items"]) 
         if x["product_id"] == item.product_id and x.get("is_weight_sale") == item.is_weight_sale),
        None
    )
    
    # Atualizar ou adicionar item
    item_data = {
        "product_id": product.id,
        "name": product.nome,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price,
        "is_weight_sale": product.venda_por_peso,
        "weight_in_kg": item.weight_in_kg if product.venda_por_peso else None,
        "custom_price": item.custom_price if product.venda_por_peso else None
    }
    
    if item_index is not None:
        # Atualizar item existente
        if product.venda_por_peso:
            # Para itens por peso, substituir completamente
            cart["items"][item_index] = item_data
        else:
            # Para itens normais, somar quantidades
            cart["items"][item_index]["quantity"] += quantity
            cart["items"][item_index]["total_price"] += total_price
    else:
        # Adicionar novo item
        cart["items"].append(item_data)
    
    # Recalcular totais
    cart["subtotal"] = sum(item["total_price"] for item in cart["items"])
    cart["total"] = cart["subtotal"]  # Sem impostos por enquanto
    
    return item_data

@router.get("", response_model=CartResponse)
async def view_cart(
    session_id: str = Header(..., alias="X-Session-ID")
) -> Any:
    """Visualiza o carrinho atual"""
    if session_id not in cart_store:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    cart = cart_store[session_id]
    return {
        "items": cart["items"],
        "subtotal": cart["subtotal"],
        "total": cart["total"]
    }

@router.post("/checkout", response_model=SaleResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Finaliza a compra e cria a venda"""
    import logging
    logger = logging.getLogger(__name__)
    
    if session_id not in cart_store:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    cart = cart_store[session_id]
    
    if not cart["items"]:
        raise HTTPException(
            status_code=400,
            detail="O carrinho está vazio"
        )
    
    logger.info(f"Iniciando checkout para carrinho: {cart}")
    
    try:
        # Cálculo dos totais (sem IVA)
        cart_data = {
            "items": cart["items"],
            "subtotal": cart["subtotal"],
            "total": cart["total"]
        }
        logger.info(f"Totais calculados: {cart_data}")
        
        # Cria a venda
        sale = Sale(
            sale_number=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status=SaleStatus.CONCLUIDA,
            subtotal=float(cart_data["subtotal"]),
            tax_amount=0.0,  # Sem IVA
            total_amount=float(cart_data["total"]),  # Total igual ao subtotal
            payment_method=PaymentMethod(checkout_data.payment_method),
            customer_id=checkout_data.customer_id,
            notes=checkout_data.notes
        )
        
        db.add(sale)
        db.flush()  # Gera o ID da venda sem fazer commit
        logger.info(f"Venda criada com ID: {sale.id}")
        
        # Adiciona os itens da venda e atualiza o estoque
        for item in cart_data["items"]:
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
                    status_code=400,
                    detail=f"Produto com ID {item['product_id']} não encontrado"
                )
            
            logger.info(f"Produto encontrado: {product.nome}, Estoque atual: {product.estoque}")
            
            # Verifica se há estoque suficiente
            if not product.venda_por_peso and product.estoque < item["quantity"]:
                db.rollback()
                logger.error(f"Estoque insuficiente para o produto {product.nome}. Estoque atual: {product.estoque}, Quantidade solicitada: {item['quantity']}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para o produto {product.nome}"
                )
            
            # Atualiza o estoque
            if not product.venda_por_peso:
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
            status_code=500,
            detail=f"Erro ao processar a venda: {str(e)}"
        )

@router.delete("/cart/items/{product_id}", response_model=dict)
async def remove_item_from_cart(
    product_id: int,
    session_id: str = Header(..., alias="X-Session-ID")
) -> dict:
    """Remove um item específico do carrinho"""
    if session_id not in cart_store or not cart_store[session_id]["items"]:
        raise HTTPException(
            status_code=404,
            detail="Carrinho não encontrado ou vazio"
        )
    
    cart = cart_store[session_id]
    initial_count = len(cart["items"])
    cart["items"][:] = [item for item in cart["items"] if item["product_id"] != product_id]
    
    if len(cart["items"]) == initial_count:
        raise HTTPException(
            status_code=404,
            detail=f"Produto com ID {product_id} não encontrado no carrinho"
        )
    
    # Recalcular totais
    cart["subtotal"] = sum(item["total_price"] for item in cart["items"])
    cart["total"] = cart["subtotal"]  # Sem impostos por enquanto
    
    return {"status": "success", "message": f"Produto {product_id} removido do carrinho"}

@router.delete("/cart", response_model=dict)
async def clear_cart(
    session_id: str = Header(..., alias="X-Session-ID")
) -> dict:
    """Remove todos os itens do carrinho"""
    if session_id in cart_store:
        cart_store[session_id] = {
            "items": [],
            "created_at": datetime.utcnow(),
            "user_id": cart_store[session_id]["user_id"]
        }
        return {"status": "success", "message": "Carrinho limpo com sucesso"}
    
    raise HTTPException(
        status_code=404,
        detail="Carrinho não encontrado"
    )
