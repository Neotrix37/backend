from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Any, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product, Category
from app.core.database import get_db
from app.core.pagination import Page, paginate

router = APIRouter()

@router.get("/", response_model=Page[ProductResponse])
async def get_products(
    search: Optional[str] = Query(None, description="Termo de busca por nome ou SKU"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    active_only: bool = Query(True, description="Mostrar apenas produtos ativos"),
    page: int = Query(1, ge=1, description="Número da página", example=1),
    size: int = Query(20, ge=1, le=100, description="Itens por página", example=20),
    db: Session = Depends(get_db)
) -> Any:
    """
    Listar produtos com filtros e paginação
    
    - **search**: Buscar por nome ou SKU (case insensitive)
    - **category_id**: Filtrar por categoria
    - **min_price**: Preço mínimo
    - **max_price**: Preço máximo
    - **active_only**: Mostrar apenas ativos (padrão: True)
    - **page**: Número da página (começando em 1)
    - **size**: Itens por página (máx 100)
    """
    query = select(Product)
    
    # Aplicar filtros
    if active_only:
        query = query.where(Product.is_active == True)  # noqa: E712
    
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        )
    
    if min_price is not None:
        query = query.where(Product.sale_price >= min_price)
    
    if max_price is not None:
        query = query.where(Product.sale_price <= max_price)
    
    # Ordenar por nome
    query = query.order_by(Product.name)
    
    # Carregar relacionamentos
    query = query.options(selectinload(Product.category))
    
    # Aplicar paginação
    return paginate(db, query, page=page, size=size)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Obter detalhes de um produto específico
    
    - **product_id**: ID do produto
    """
    query = select(Product).where(Product.id == product_id)
    query = query.options(selectinload(Product.category))
    
    product = db.execute(query).scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Criar um novo produto
    
    - **product_data**: Dados do produto a ser criado
    """
    # Verificar se já existe produto com o mesmo SKU
    existing = db.execute(
        select(Product).where(Product.sku == product_data.sku)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto com este SKU"
        )
    
    # Verificar se a categoria existe
    if product_data.category_id:
        category = db.get(Category, product_data.category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria inválida ou inativa"
            )
    
    # Criar o produto
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int, 
    product_data: ProductUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Atualizar um produto existente
    
    - **product_id**: ID do produto a ser atualizado
    - **product_data**: Dados para atualização
    """
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Verificar se o novo SKU já existe
    if product_data.sku and product_data.sku != product.sku:
        existing = db.execute(
            select(Product).where(Product.sku == product_data.sku)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um produto com este SKU"
            )
    
    # Verificar se a categoria existe
    if product_data.category_id is not None and product_data.category_id != product.category_id:
        category = db.get(Category, product_data.category_id)
        if not category or not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria inválida ou inativa"
            )
    
    # Atualizar os campos
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int, 
    db: Session = Depends(get_db)
) -> None:
    """
    Excluir um produto (soft delete)
    
    - **product_id**: ID do produto a ser excluído
    """
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Soft delete
    product.is_active = False
    db.commit()

@router.get("/{product_id}/stock", response_model=dict)
async def get_product_stock(
    product_id: int, 
    db: Session = Depends(get_db)
) -> dict:
    """
    Obter informações de estoque de um produto
    
    - **product_id**: ID do produto
    
    Retorna:
    ```json
    {
        "product_id": 1,
        "product_name": "Produto A",
        "current_stock": 100,
        "min_stock": 10,
        "status": "ok" | "low" | "critical"
    }
    ```
    """
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Determinar status do estoque
    if product.current_stock <= 0:
        status = "out_of_stock"
    elif product.current_stock <= product.min_stock * 0.3:  # 30% do estoque mínimo
        status = "critical"
    elif product.current_stock <= product.min_stock:
        status = "low"
    else:
        status = "ok"
    
    return {
        "product_id": product.id,
        "product_name": product.name,
        "current_stock": product.current_stock,
        "min_stock": product.min_stock,
        "status": status
    }
