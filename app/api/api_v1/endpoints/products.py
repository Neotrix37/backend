from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.database import get_db
from app.models.product import Product
from app.models.category import Category

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
	skip: int = Query(0, ge=0, description="Número de registros para pular"),
	limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
	search: Optional[str] = Query(None, description="Termo de busca por nome ou código"),
	category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
	include_inactive: bool = Query(False, description="Incluir produtos inativos"),
	sort_by: str = Query("nome", description="Campo para ordenação: nome, codigo, preco_venda"),
	sort_order: str = Query("asc", description="Ordem de classificação: asc, desc"),
	db: Session = Depends(get_db)
) -> Any:
	query = select(Product)
	
	# Filtra por status ativo/inativo
	if not include_inactive:
		query = query.where(Product.is_active == True)  # noqa: E712
	
	# Outros filtros
	if category_id is not None:
		query = query.where(Product.category_id == category_id)
	if search:
		like = f"%{search}%"
		query = query.where(
			or_(
				Product.nome.ilike(like), 
				Product.codigo.ilike(like)
			)
		)
	
	# Ordenação
	if sort_by == "nome":
		query = query.order_by(Product.nome.asc() if sort_order == "asc" else Product.nome.desc())
	elif sort_by == "codigo":
		query = query.order_by(Product.codigo.asc() if sort_order == "asc" else Product.codigo.desc())
	elif sort_by == "preco_venda":
		query = query.order_by(Product.preco_venda.asc() if sort_order == "asc" else Product.preco_venda.desc())
	else:
		# Ordenação padrão por nome (A-Z)
		query = query.order_by(Product.nome.asc())

	query = query.offset(skip).limit(limit)
	products = db.execute(query).scalars().all()
	return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)) -> Any:
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)
	return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)) -> Any:
    # Verifica se já existe um produto com o mesmo código
    existing_product = db.query(Product).filter(
        Product.codigo == product_data.codigo
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto com este código"
        )

    # Cria a entidade com os novos nomes de campos
    product = Product(
        nome=product_data.nome,
        descricao=product_data.descricao,
        codigo=product_data.codigo,
        preco_compra=product_data.preco_compra,
        preco_venda=product_data.preco_venda,
        estoque=product_data.estoque,
        estoque_minimo=product_data.estoque_minimo,
        category_id=product_data.category_id,
        venda_por_peso=product_data.venda_por_peso,
        is_active=True  # Ativo por padrão
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Converte para dicionário para garantir que todos os campos sejam serializados
        response_data = {
            'id': product.id,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
            'is_active': product.is_active,
            'codigo': product.codigo,
            'category_id': product.category_id,
            'nome': product.nome,
            'descricao': product.descricao,
            'preco_compra': str(product.preco_compra),  # Convertendo para string para evitar problemas de serialização
            'preco_venda': str(product.preco_venda),
            'estoque': product.estoque,
            'estoque_minimo': product.estoque_minimo,
            'venda_por_peso': product.venda_por_peso,
            # Campos antigos para compatibilidade
            'sku': product.codigo,
            'name': product.nome,
            'cost_price': str(product.preco_compra),
            'sale_price': str(product.preco_venda),
            'current_stock': product.estoque,
            'min_stock': product.estoque_minimo
        }
        
        return response_data
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar produto: {str(e)}"
        )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)) -> Any:
	# Busca o produto
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)

	update_data = product_data.model_dump(exclude_unset=True)
	
	# Valida a categoria se for fornecida
	if 'category_id' in update_data and update_data['category_id'] is not None and update_data['category_id'] != 0:
		category = db.get(Category, update_data['category_id'])
		if not category:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Categoria com ID {update_data['category_id']} não encontrada"
			)
	
	# Valida código único se estiver sendo atualizado
	if 'codigo' in update_data and update_data['codigo']:
		existing_product = db.query(Product).filter(
			Product.codigo == update_data['codigo'],
			Product.id != product_id
		).first()
		
		if existing_product:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Já existe um produto com este código"
			)

	# Atualiza os campos
	for field, value in update_data.items():
		setattr(product, field, value)

	try:
		db.commit()
		db.refresh(product)
	except Exception as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Erro ao atualizar produto: {str(e)}"
		)

	return product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
	"""
	Desativa um produto (exclusão lógica).
	"""
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)

	if not product.is_active:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Este produto já está desativado"
		)

	try:
		# Marca como inativo em vez de excluir
		product.is_active = False
		db.commit()
		return {
			"status": "success", 
			"message": "Produto desativado com sucesso",
			"product_id": product_id
		}
	except Exception as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Erro ao desativar produto: {str(e)}"
		)


@router.get("/{product_id}/estoque", response_model=dict)
async def get_product_stock(product_id: int, db: Session = Depends(get_db)) -> dict:
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)

	return {
		"product_id": product.id,
		"nome": product.nome,
		"codigo": product.codigo,
		"estoque_atual": product.estoque,
		"estoque_minimo": product.estoque_minimo,
		"status_estoque": "CRÍTICO" if product.estoque <= product.estoque_minimo else "OK"
	}


@router.post("/{product_id}/activate", status_code=status.HTTP_200_OK)
async def activate_product(product_id: int, db: Session = Depends(get_db)) -> dict:
	"""
	Reativa um produto previamente desativado.
	"""
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)

	if product.is_active:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Este produto já está ativo"
		)

	try:
		# Reativa o produto
		product.is_active = True
		db.commit()
		return {
			"status": "success", 
			"message": "Produto reativado com sucesso",
			"product_id": product_id
		}
	except Exception as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Erro ao reativar produto: {str(e)}"
		)
