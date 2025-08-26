from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.database import get_db
from app.models.product import Product
from app.models.category import Category

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
	skip: int = Query(0, ge=0, description="Número de registros para pular"),
	limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
	search: Optional[str] = Query(None, description="Termo de busca por nome ou SKU"),
	category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
	active_only: bool = Query(True, description="Mostrar apenas produtos ativos"),
	db: Session = Depends(get_db)
) -> Any:
	query = select(Product)
	if active_only:
		query = query.where(Product.is_active == True)  # noqa: E712
	if category_id is not None:
		query = query.where(Product.category_id == category_id)
	if search:
		like = f"%{search}%"
		query = query.where((Product.name.ilike(like)) | (Product.sku.ilike(like)))

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
	# Cria a entidade
	product = Product(
		name=product_data.name,
		description=product_data.description,
		sku=product_data.sku,
		cost_price=product_data.cost_price,
		sale_price=product_data.sale_price,
		current_stock=product_data.current_stock,
		min_stock=product_data.min_stock,
		category_id=product_data.category_id,
		venda_por_peso=product_data.venda_por_peso
	)
	# Ativo por padrão
	product.is_active = True

	db.add(product)
	db.commit()
	db.refresh(product)
	return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)) -> Any:
	# Busca o produto
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)

	# Valida a categoria se for fornecida
	if product_data.category_id is not None and product_data.category_id != 0:
		category = db.get(Category, product_data.category_id)
		if not category:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Categoria com ID {product_data.category_id} não encontrada"
			)

	# Atualiza apenas os campos fornecidos
	update_data = product_data.model_dump(exclude_unset=True)
	
	# Remove category_id se for 0 (valor padrão do Swagger)
	if 'category_id' in update_data and update_data['category_id'] == 0:
		update_data['category_id'] = None
	
	for field, value in update_data.items():
		setattr(product, field, value)

	db.add(product)
	db.commit()
	db.refresh(product)
	return product


@router.delete("/delete-all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_products(db: Session = Depends(get_db)):
	# Soft delete de todos os produtos
	db.query(Product).update({Product.is_active: False})
	db.commit()


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)
	# Soft delete
	product.is_active = False
	db.add(product)
	db.commit()


@router.get("/{product_id}/stock", response_model=dict)
async def get_product_stock(product_id: int, db: Session = Depends(get_db)) -> Any:
	product = db.get(Product, product_id)
	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Produto não encontrado"
		)
	return {
		"product_id": product.id,
		"name": product.name,
		"current_stock": product.current_stock,
		"min_stock": product.min_stock,
		"stock_status": "low" if product.current_stock <= product.min_stock else "ok",
	}
