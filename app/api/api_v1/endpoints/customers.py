from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.models.customer import Customer
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(db: Session = Depends(get_db)) -> Any:
    """Listar todos os clientes"""
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter cliente por ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_active == True).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return customer

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)) -> Any:
    """Criar novo cliente"""
    # Verificar se já existe cliente com o mesmo CPF/CNPJ
    existing_customer = db.query(Customer).filter(
        Customer.cpf_cnpj == customer_data.cpf_cnpj,
        Customer.is_active == True
    ).first()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cliente com este CPF/CNPJ"
        )
    
    new_customer = Customer(**customer_data.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)) -> Any:
    """Atualizar cliente existente"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_active == True).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se o novo CPF/CNPJ já existe em outro cliente
    if customer_data.cpf_cnpj:
        existing_customer = db.query(Customer).filter(
            Customer.cpf_cnpj == customer_data.cpf_cnpj,
            Customer.id != customer_id,
            Customer.is_active == True
        ).first()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este CPF/CNPJ"
            )
    
    # Atualizar campos
    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Deletar cliente (soft delete)"""
    customer = db.query(Customer).filter(Customer.id == customer_id, Customer.is_active == True).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Soft delete
    customer.is_active = False
    db.commit()
