from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import sqlalchemy.orm
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
from app.models.user import User
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
    current_user: User = Depends(get_current_active_user)
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
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "is_weight_sale": product.venda_por_peso,
            "weight_in_kg": float(item.weight_in_kg) if product.venda_por_peso and item.weight_in_kg is not None else None,
            "custom_price": float(item.custom_price) if product.venda_por_peso and item.custom_price is not None else None
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
    session_id: str = Header(..., alias="X-Session-ID")
) -> Any:
    """Visualiza o carrinho atual"""
    try:
        logger.info(f"Visualizando carrinho. Sessão: {session_id}")
        
        if session_id not in cart_store:
            logger.info("Carrinho não encontrado, retornando carrinho vazio")
            return {
                "items": [],
                "subtotal": 0.0,
                "total": 0.0,
                "tax_amount": 0.0
            }
        
        cart = cart_store[session_id]
        logger.info(f"Carrinho encontrado: {cart}")
        
        return {
            "items": cart["items"],
            "subtotal": cart.get("subtotal", 0.0),
            "total": cart.get("total", 0.0),
            "tax_amount": cart.get("tax_amount", 0.0)
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
    current_user: User = Depends(get_current_active_user)
):
    """Finaliza a compra e cria a venda"""
    try:
        logger.info(f"Iniciando checkout. Sessão: {session_id}, Usuário: {current_user.id}")
        logger.info(f"Dados do checkout: {checkout_data.dict()}")
        
        if session_id not in cart_store:
            logger.error("Carrinho não encontrado")
            raise HTTPException(status_code=404, detail="Carrinho não encontrado")
        
        cart = cart_store[session_id]
        logger.info(f"Carrinho encontrado: {cart}")
        
        if not cart["items"]:
            logger.error("Carrinho vazio")
            raise HTTPException(
                status_code=400,
                detail="O carrinho está vazio"
            )
        
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
            notes=checkout_data.notes,
            user_id=current_user.id
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
            
            # Cria o item da venda com todos os campos necessários
            sale_item_data = {
                "sale_id": sale.id,
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": float(item["unit_price"]),
                "total_price": float(item["total_price"]),
                "is_weight_sale": item.get("is_weight_sale", False),
                "weight_in_kg": item.get("weight_in_kg"),
                "custom_price": item.get("custom_price")
            }
            
            # Criamos o item da venda com todos os campos
            sale_item = SaleItem(**sale_item_data)
            db.add(sale_item)
            logger.info(f"Item de venda criado: {sale_item}")
        
        # Confirma a transação
        db.commit()
        logger.info("Transação confirmada com sucesso")
        
        # Carrega a venda com todos os itens e seus produtos relacionados
        # Usando joinedload para garantir que product.nome esteja disponível para o Pydantic
        sale_with_items = db.query(Sale).options(
            sqlalchemy.orm.joinedload(Sale.items).joinedload(SaleItem.product),
            sqlalchemy.orm.joinedload(Sale.user)
        ).filter(Sale.id == sale.id).first()
        
        # Garantir que todos os relacionamentos estejam carregados e adicionar product_name
        for item in sale_with_items.items:
            # Acessar o nome do produto para garantir que está carregado
            if item.product:
                # Adicionar o nome do produto diretamente ao item para facilitar a serialização
                item.product_name = item.product.nome
        
        # Limpa o carrinho após a finalização
        cart_store.pop(session_id, None)
        logger.info("Carrinho limpo após finalização")
        
        # Criar a resposta com a mensagem de sucesso
        sale_with_items.message = "Venda finalizada com sucesso!"
        
        return sale_with_items
        
    except HTTPException as he:
        logger.error(f"Erro HTTP: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a venda: {str(e)}"
        )

@router.delete("/items/{product_id}", response_model=dict)
async def remove_item_from_cart(
    product_id: int,
    session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    current_user: User = Depends(get_current_active_user)
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
