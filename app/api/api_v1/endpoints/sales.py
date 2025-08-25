from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse
from app.models.sale import Sale
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[SaleResponse])
async def get_sales(db: Session = Depends(get_db)) -> Any:
    """Listar todas as vendas"""
    sales = db.query(Sale).filter(Sale.is_active == True).all()
    return sales

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(sale_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter venda por ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.is_active == True).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    return sale

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)) -> Any:
    """Criar nova venda"""
    # Gerar número de venda único
    last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
    if last_sale:
        last_number = int(last_sale.sale_number[1:]) if last_sale.sale_number.startswith('V') else 0
        new_number = f"V{last_number + 1:03d}"
    else:
        new_number = "V001"
    
    # Criar venda
    sale_dict = sale_data.model_dump()
    sale_dict['sale_number'] = new_number
    new_sale = Sale(**sale_dict)
    
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    
    return new_sale

@router.put("/{sale_id}", response_model=SaleResponse)
async def update_sale(sale_id: int, sale_data: SaleUpdate, db: Session = Depends(get_db)) -> Any:
    """Atualizar venda existente"""
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.is_active == True).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Atualizar campos
    for field, value in sale_data.model_dump(exclude_unset=True).items():
        setattr(sale, field, value)
    
    db.commit()
    db.refresh(sale)
    
    return sale

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    """Deletar venda (soft delete)"""
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.is_active == True).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venda não encontrada"
        )
    
    # Soft delete
    sale.is_active = False
    db.commit()
