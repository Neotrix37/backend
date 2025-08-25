from datetime import date, timedelta
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_

from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerType
from app.models.customer import Customer
from app.core.database import get_db
from app.core.pagination import Page, paginate

router = APIRouter()

@router.get("/", response_model=Page[CustomerResponse])
async def get_customers(
    search: Optional[str] = Query(None, description="Termo de busca por nome, CPF/CNPJ ou email"),
    customer_type: Optional[CustomerType] = Query(None, description="Tipo de cliente (individual ou business)"),
    is_active: Optional[bool] = Query(True, description="Filtrar por status (ativo/inativo)"),
    registration_date_start: Optional[date] = Query(None, description="Data de cadastro inicial (YYYY-MM-DD)"),
    registration_date_end: Optional[date] = Query(None, description="Data de cadastro final (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página", example=1),
    size: int = Query(20, ge=1, le=100, description="Itens por página", example=20),
    db: Session = Depends(get_db)
) -> Any:
    """
    Listar clientes com filtros e paginação
    
    - **search**: Buscar por nome, CPF/CNPJ ou email (case insensitive)
    - **customer_type**: Filtrar por tipo (individual ou business)
    - **is_active**: Filtrar por status (true=ativo, false=inativo)
    - **registration_date_start**: Filtrar a partir desta data de cadastro
    - **registration_date_end**: Filtrar até esta data de cadastro
    - **page**: Número da página (começando em 1)
    - **size**: Itens por página (máx 100)
    """
    query = select(Customer)
    
    # Aplicar filtros
    if is_active is not None:
        query = query.where(Customer.is_active == is_active)
    
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    
    if registration_date_start:
        query = query.where(Customer.created_at >= registration_date_start)
    
    if registration_date_end:
        # Adiciona 1 dia para incluir o dia final
        query = query.where(Customer.created_at < registration_date_end + timedelta(days=1))
    
    if search:
        search_term = f"%{search}%"
        search_filters = [
            Customer.name.ilike(search_term),
            Customer.email.ilike(search_term) if Customer.email is not None else False
        ]
        
        # Formatar CPF/CNPJ para busca (removendo formatação)
        clean_search = search.replace(" ", "").replace("-", "").replace(".", "").replace("/", "")
        if clean_search.isdigit():
            search_filters.append(Customer.cpf_cnpj.contains(clean_search))
        
        query = query.where(or_(*[f for f in search_filters if f is not False]))
    
    # Ordenar por nome
    query = query.order_by(Customer.name)
    
    # Aplicar paginação
    return paginate(db, query, page=page, size=size)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Obter detalhes de um cliente específico
    
    - **customer_id**: ID do cliente
    """
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.execute(query).scalar_one_or_none()
    
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return customer

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Criar um novo cliente
    
    - **customer_data**: Dados do cliente a ser criado
    """
    # Validar CPF/CNPJ
    if customer_data.customer_type == "individual" and len(customer_data.cpf_cnpj) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF inválido. Deve conter 11 dígitos."
        )
    elif customer_data.customer_type == "business" and len(customer_data.cpf_cnpj) != 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ inválido. Deve conter 14 dígitos."
        )
    
    # Verificar se já existe cliente com o mesmo CPF/CNPJ
    existing = db.execute(
        select(Customer).where(Customer.cpf_cnpj == customer_data.cpf_cnpj)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um cliente com este {'CPF' if customer_data.customer_type == 'individual' else 'CNPJ'}"
        )
    
    # Verificar se já existe cliente com o mesmo email
    if customer_data.email:
        existing = db.execute(
            select(Customer).where(Customer.email == customer_data.email)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este email"
            )
    
    # Criar o cliente
    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int, 
    customer_data: CustomerUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Atualizar um cliente existente
    
    - **customer_id**: ID do cliente a ser atualizado
    - **customer_data**: Dados para atualização
    """
    customer = db.get(Customer, customer_id)
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    update_data = customer_data.model_dump(exclude_unset=True)
    
    # Validar CPF/CNPJ se for fornecido
    if 'cpf_cnpj' in update_data:
        cpf_cnpj = update_data['cpf_cnpj']
        customer_type = update_data.get('customer_type', customer.customer_type)
        
        if customer_type == "individual" and len(cpf_cnpj) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF inválido. Deve conter 11 dígitos."
            )
        elif customer_type == "business" and len(cpf_cnpj) != 14:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ inválido. Deve conter 14 dígitos."
            )
        
        # Verificar se o novo CPF/CNPJ já existe
        if cpf_cnpj != customer.cpf_cnpj:
            existing = db.execute(
                select(Customer).where(Customer.cpf_cnpj == cpf_cnpj)
            ).scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Já existe um cliente com este {'CPF' if customer_type == 'individual' else 'CNPJ'}"
                )
    
    # Verificar se o novo email já existe
    if 'email' in update_data and update_data['email'] != customer.email:
        existing = db.execute(
            select(Customer).where(Customer.email == update_data['email'])
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este email"
            )
    
    # Atualizar os campos
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int, 
    db: Session = Depends(get_db)
) -> None:
    """
    Excluir um cliente (soft delete)
    
    - **customer_id**: ID do cliente a ser excluído
    """
    customer = db.get(Customer, customer_id)
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se o cliente tem vendas associadas
    if customer.sales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir um cliente com vendas associadas"
        )
    
    # Soft delete
    customer.is_active = False
    db.commit()
