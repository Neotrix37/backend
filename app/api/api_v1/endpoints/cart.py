from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.models.sale_item import SaleItem
from app.schemas.sale import CartItemCreate, CartResponse, CheckoutRequest, SaleResponse, PaymentMethod, CartItemResponse
from app.models.user import User as UserModel
from app.core.security import get_current_active_user

router = APIRouter(tags=["cart"])

# Armazenamento temporário do carrinho (em produção, use Redis ou banco de dados)
cart_store: Dict[str, Dict[str, Any]] = {}

def get_or_create_cart(session_id: str, user_id: int) -> Dict[str, Any]:
    """Obtém ou cria um carrinho para a sessão"""
    if session_id not in cart_store:
        cart_store[session_id] = {
            "items": [],
            "created_at": datetime.utcnow(),
            "user_id": user_id,
            "subtotal": 0.0,
            "total": 0.0
        }
    return cart_store[session_id]

@router.post("/add", response_model=CartItemResponse)
async def add_to_cart(
    item: CartItemCreate,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Adiciona um item ao carrinho"""
    try:
        logger.info(f"Iniciando adição ao carrinho. Sessão: {session_id}, Usuário: {current_user.id}")
        logger.info(f"Dados do item: {item.dict()}")
        
        # Obter o produto
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_active == True
        ).first()
        
        if not product:
            logger.error(f"Produto não encontrado ou inativo. ID: {item.product_id}")
            raise HTTPException(status_code=404, detail="Produto não encontrado ou inativo")
        
        logger.info(f"Produto encontrado: {product.nome} (ID: {product.id})")
        
        # Verificar se é venda por peso
        if product.venda_por_peso:
            logger.info("Produto com venda por peso")
            if not item.is_weight_sale or item.weight_in_kg is None or item.custom_price is None:
                error_msg = "Para produtos vendidos por peso, é necessário informar o peso e o preço personalizado"
                logger.error(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Usar o peso informado para a quantidade
            quantity = float(item.weight_in_kg)
            unit_price = float(item.custom_price) / quantity if quantity > 0 else 0
            total_price = float(item.custom_price)
            logger.info(f"Venda por peso - Peso: {quantity}kg, Preço total: {total_price}, Preço unitário: {unit_price}")
        else:
            # Venda normal por unidade
            quantity = float(item.quantity)
            try:
                # Converter o preco_venda para float, tratando diferentes tipos
                preco_venda = float(str(product.preco_venda).replace(',', '.'))
                unit_price = preco_venda
                total_price = unit_price * quantity
                logger.info(f"Venda por unidade - Quantidade: {quantity}, Preço unitário: {unit_price}, Total: {total_price}")
            except (ValueError, TypeError) as e:
                error_msg = f"Erro ao converter preço do produto: {str(e)}"
                logger.error(f"{error_msg}. Valor de preco_venda: {product.preco_venda}, Tipo: {type(product.preco_venda)}")
                raise HTTPException(status_code=500, detail=error_msg)
        
        # Verificar estoque (se aplicável)
        if not product.venda_por_peso and product.estoque < quantity:
            error_msg = f"Estoque insuficiente. Disponível: {product.estoque}, Solicitado: {quantity}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
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
            "nome": product.nome,
            "sku": product.codigo,  # Usando o campo correto do modelo
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "is_weight_sale": product.venda_por_peso,
            "weight_in_kg": float(item.weight_in_kg) if product.venda_por_peso and item.weight_in_kg is not None else None,
            "custom_price": float(item.custom_price) if product.venda_por_peso and item.custom_price is not None else None,
            "estoque_disponivel": product.estoque  # Add available stock to the item data
        }
        
        if item_index is not None:
            # Atualizar item existente
            if product.venda_por_peso:
                # Para itens por peso, substituir completamente
                cart["items"][item_index] = item_data
            else:
                # Para itens normais, verificar se é para atualizar ou adicionar
                if getattr(item, 'update_quantity', False):
                    # Atualiza a quantidade para o valor exato
                    cart["items"][item_index]["quantity"] = quantity
                    cart["items"][item_index]["total_price"] = unit_price * quantity
                else:
                    # Soma as quantidades (comportamento atual)
                    cart["items"][item_index]["quantity"] += quantity
                    cart["items"][item_index]["total_price"] += total_price
                
                # Atualiza o estoque disponível
                cart["items"][item_index]["estoque_disponivel"] = product.estoque
        else:
            # Adicionar novo item
            cart["items"].append(item_data)
        
        # Recalcular totais
        cart["subtotal"] = sum(item["total_price"] for item in cart["items"])
        cart["total"] = cart["subtotal"]  # Sem impostos por enquanto
        
        return item_data
        
    except HTTPException as he:
        logger.error(f"Erro HTTP: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar o item no carrinho: {str(e)}"
        )

@router.get("", response_model=CartResponse)
async def view_cart(
    session_id: str = Header(..., alias="X-Session-ID"),
    current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    """Visualiza o carrinho atual"""
    try:
        logger.info(f"Visualizando carrinho. Sessão: {session_id}, Usuário: {current_user.id}")
        
        if session_id not in cart_store:
            logger.info("Carrinho não encontrado, retornando carrinho vazio")
            return {
                "items": [],
                "subtotal": 0.0,
                "total": 0.0
            }
        
        cart = cart_store[session_id]
        logger.info(f"Carrinho encontrado: {cart}")
        
        return {
            "items": cart["items"],
            "subtotal": cart["subtotal"],
            "total": cart["total"]
        }
        
    except HTTPException as he:
        logger.error(f"Erro HTTP: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao visualizar o carrinho: {str(e)}"
        )

@router.post("/checkout", response_model=SaleResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Finaliza a compra e cria a venda"""
    try:
        logger.info(f"Iniciando checkout. Sessão: {session_id}, Usuário: {current_user.id}")
        
        if session_id not in cart_store:
            logger.error("Carrinho não encontrado")
            raise HTTPException(status_code=404, detail="Carrinho não encontrado")
        
        cart = cart_store[session_id]
        
        if not cart["items"]:
            logger.error("Carrinho vazio")
            raise HTTPException(status_code=400, detail="O carrinho está vazio")
        
        # Start transaction
        db.begin()
        
        try:
            # Create sale
            sale = Sale(
                sale_number=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
                status=SaleStatus.CONCLUIDA,
                subtotal=float(cart["subtotal"]),
                tax_amount=0.0,
                discount_amount=0.0,
                total_amount=float(cart["total"]),
                payment_method=checkout_data.payment_method,
                customer_id=checkout_data.customer_id,
                notes=checkout_data.notes,
                user_id=current_user.id
            )
            db.add(sale)
            db.flush()
            
            # Process items
            for item in cart["items"]:
                product = db.query(Product).filter(
                    Product.id == item["product_id"],
                    Product.is_active == True
                ).with_for_update().first()
                
                if not product:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Produto com ID {item['product_id']} não encontrado ou inativo"
                    )
                
                # Update stock if not sold by weight
                if not product.venda_por_peso:
                    if product.estoque < item["quantity"]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Estoque insuficiente para o produto {product.nome}"
                        )
                    product.estoque -= item["quantity"]
                    db.add(product)
                
                # Create sale item
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    unit_price=float(item["unit_price"]),
                    total_price=float(item["total_price"])
                )
                db.add(sale_item)
            
            # Commit transaction
            db.commit()
            
            # Clear cart
            cart_store.pop(session_id, None)
            
            # Reload sale with relationships
            sale = db.query(Sale).options(
                joinedload(Sale.items).joinedload(SaleItem.product)
            ).filter(Sale.id == sale.id).first()
            
            if not sale:
                raise HTTPException(
                    status_code=500,
                    detail="Erro ao recuperar os dados da venda"
                )
            
            # Prepare response
            response_items = []
            for item in sale.items:
                response_items.append({
                    "id": item.id,
                    "product_id": item.product_id,
                    "product": {
                        "id": item.product.id,
                        "nome": item.product.nome,
                        "codigo": item.product.codigo,
                        "preco_venda": float(item.product.preco_venda),
                        "venda_por_peso": item.product.venda_por_peso,
                        "unidade_medida": item.product.unidade_medida,
                        "estoque_atual": float(item.product.estoque) if not item.product.venda_por_peso else None
                    },
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.total_price),
                    "is_weight_sale": item.product.venda_por_peso,
                    "weight_in_kg": float(item.quantity) if item.product.venda_por_peso else None,
                    "custom_price": float(item.unit_price) if item.product.venda_por_peso else None,
                    "created_at": item.created_at
                })
            
            response_data = {
                "id": sale.id,
                "sale_number": sale.sale_number,
                "status": sale.status,
                "subtotal": float(sale.subtotal),
                "tax_amount": float(sale.tax_amount),
                "discount_amount": float(sale.discount_amount),
                "total_amount": float(sale.total_amount),
                "payment_method": sale.payment_method,
                "created_at": sale.created_at,
                "items": response_items
            }
            
            return response_data
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro durante o checkout: {str(e)}", exc_info=True)
            raise
            
    except HTTPException as he:
        logger.error(f"Erro HTTP: {str(he.detail)}")
        raise
        
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        if db.in_transaction():
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a venda: {str(e)}"
        )

@router.delete("/items/{product_id}", response_model=dict)
async def remove_item_from_cart(
    product_id: int,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
) -> dict:
    """Remove um item específico do carrinho"""
    try:
        logger.info(f"Removendo item do carrinho. Sessão: {session_id}, Produto: {product_id}")
        
        if session_id not in cart_store or not cart_store.get(session_id, {}).get("items"):
            logger.info("Carrinho não encontrado ou vazio")
            return {
                "status": "success", 
                "message": "Carrinho não encontrado ou já está vazio",
                "items": []
            }
        
        cart = cart_store[session_id]
        initial_count = len(cart["items"])
        cart["items"][:] = [
            item for item in cart["items"] 
            if str(item["product_id"]) != str(product_id)
        ]
        
        if len(cart["items"]) == initial_count:
            logger.info(f"Produto com ID {product_id} não encontrado no carrinho")
            return {
                "status": "success",
                "message": f"Produto {product_id} não encontrado no carrinho",
                "items": cart["items"]
            }
        
        # Recalcular totais
        cart["subtotal"] = sum(item["total_price"] for item in cart["items"])
        cart["total"] = cart["subtotal"]  # Sem impostos por enquanto
        
        logger.info(f"Carrinho após remoção: {cart}")
        
        return {
            "status": "success", 
            "message": f"Produto {product_id} removido do carrinho",
            "items": cart["items"]
        }
        
    except Exception as e:
        logger.error(f"Erro inesperado ao remover item do carrinho: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover o item do carrinho: {str(e)}"
        )

@router.delete("", response_model=dict)
async def clear_cart(
    session_id: str = Header(..., alias="X-Session-ID"),
    current_user: UserModel = Depends(get_current_active_user)
) -> dict:
    """Remove todos os itens do carrinho"""
    try:
        logger.info(f"Limpando carrinho. Sessão: {session_id}")
        
        if session_id not in cart_store:
            logger.info("Carrinho não encontrado")
            return {
                "status": "success",
                "message": "Carrinho não encontrado ou já está vazio",
                "items": []
            }
        
        # Salva o user_id antes de limpar
        user_id = cart_store[session_id].get("user_id", current_user.id)
        
        # Cria um novo carrinho vazio
        cart_store[session_id] = {
            "items": [],
            "created_at": datetime.utcnow(),
            "user_id": user_id,
            "subtotal": 0.0,
            "total": 0.0
        }
        
        logger.info("Carrinho limpo com sucesso")
        return {
            "status": "success",
            "message": "Carrinho limpo com sucesso",
            "items": []
        }
        
    except Exception as e:
        logger.error(f"Erro inesperado ao limpar carrinho: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar o carrinho: {str(e)}"
        )
