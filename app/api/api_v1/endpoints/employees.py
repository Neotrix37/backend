from datetime import date
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee, EmployeeRole
from app.core.database import get_db
from app.core.pagination import Page, paginate

router = APIRouter()

@router.get("/", response_model=Page[EmployeeResponse])
async def get_employees(
    search: Optional[str] = Query(None, description="Termo de busca por nome, CPF ou email"),
    role: Optional[EmployeeRole] = Query(None, description="Filtrar por cargo"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status (ativo/inativo)"),
    hire_date_start: Optional[date] = Query(None, description="Data de admissão inicial (YYYY-MM-DD)"),
    hire_date_end: Optional[date] = Query(None, description="Data de admissão final (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página", example=1),
    size: int = Query(20, ge=1, le=100, description="Itens por página", example=20),
    db: Session = Depends(get_db)
) -> Any:
    """
    Listar funcionários com filtros e paginação
    
    - **search**: Buscar por nome, CPF ou email (case insensitive)
    - **role**: Filtrar por cargo (ex: manager, cashier, stockist, admin)
    - **is_active**: Filtrar por status (true=ativo, false=inativo)
    - **hire_date_start**: Filtrar a partir desta data de admissão
    - **hire_date_end**: Filtrar até esta data de admissão
    - **page**: Número da página (começando em 1)
    - **size**: Itens por página (máx 100)
    """
    query = select(Employee)
    
    # Aplicar filtros
    if is_active is not None:
        query = query.where(Employee.is_active == is_active)
    
    if role:
        query = query.where(Employee.role == role)
    
    if hire_date_start:
        query = query.where(Employee.hire_date >= hire_date_start)
    
    if hire_date_end:
        query = query.where(Employee.hire_date <= hire_date_end)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Employee.name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.cpf.like(search_term.replace(" ", "").replace("-", "").replace(".", ""))
            )
        )
    
    # Ordenar por nome
    query = query.order_by(Employee.name)
    
    # Aplicar paginação
    return paginate(db, query, page=page, size=size)

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Obter detalhes de um funcionário específico
    
    - **employee_id**: ID do funcionário
    """
    query = select(Employee).where(Employee.id == employee_id)
    employee = db.execute(query).scalar_one_or_none()
    
    if not employee or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    return employee

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Criar um novo funcionário
    
    - **employee_data**: Dados do funcionário a ser criado
    """
    # Verificar se já existe funcionário com o mesmo CPF
    existing = db.execute(
        select(Employee).where(Employee.cpf == employee_data.cpf)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um funcionário com este CPF"
        )
    
    # Verificar se já existe funcionário com o mesmo email
    if employee_data.email:
        existing = db.execute(
            select(Employee).where(Employee.email == employee_data.email)
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um funcionário com este email"
            )
    
    # Criar o funcionário
    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    return employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int, 
    employee_data: EmployeeUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Atualizar um funcionário existente
    
    - **employee_id**: ID do funcionário a ser atualizado
    - **employee_data**: Dados para atualização
    """
    employee = db.get(Employee, employee_id)
    if not employee or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    update_data = employee_data.model_dump(exclude_unset=True)
    
    # Verificar se o novo CPF já existe
    if 'cpf' in update_data and update_data['cpf'] != employee.cpf:
        existing = db.execute(
            select(Employee).where(Employee.cpf == update_data['cpf'])
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um funcionário com este CPF"
            )
    
    # Verificar se o novo email já existe
    if 'email' in update_data and update_data['email'] != employee.email:
        existing = db.execute(
            select(Employee).where(Employee.email == update_data['email'])
        ).scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um funcionário com este email"
            )
    
    # Atualizar os campos
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db)
) -> None:
    """
    Excluir um funcionário (soft delete)
    
    - **employee_id**: ID do funcionário a ser excluído
    """
    employee = db.get(Employee, employee_id)
    if not employee or not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Soft delete
    employee.is_active = False
    db.commit()
