from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional, Any
from sqlalchemy.orm import Session

from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.database import get_db
from app.models.category import Category

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as categorias ativas"""
    query = db.query(Category)
    
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
        
    return query.offset(skip).limit(limit).all()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Obtém uma categoria pelo ID"""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    return category

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)) -> Any:
    """Criar nova categoria"""
    # Verificar se já existe categoria com o mesmo nome
    existing_category = db.query(Category).filter(
        Category.name == category_data.name,
        Category.is_active == True
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma categoria com este nome"
        )
    
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)) -> Any:
    """Atualizar categoria existente"""
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Verificar se o novo nome já existe em outra categoria
    if category_data.name:
        existing_category = db.query(Category).filter(
            Category.name == category_data.name,
            Category.id != category_id,
            Category.is_active == True
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma categoria com este nome"
            )
    
    # Atualizar campos
    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Deletar categoria (soft delete)"""
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Soft delete
    category.is_active = False
    db.commit()
