from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee
from app.core.database import get_db
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    show_inactive: bool = False,
    db: Session = Depends(get_db)
) -> Any:
    """Listar funcionários ativos ou todos (incluindo inativos), ordenados alfabeticamente"""
    query = db.query(Employee)
    
    # Filtrar apenas ativos se show_inactive for False
    if not show_inactive:
        query = query.filter(Employee.is_active == True)
    
    # Ordenar por nome completo em ordem alfabética
    query = query.order_by(Employee.full_name.asc())
        
    employees = query.all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter funcionário por ID"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id, 
        Employee.is_active == True
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    return employee

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)) -> Any:
    """Criar novo funcionário"""
    # Garantir que o username comece com letra maiúscula
    if employee_data.username and len(employee_data.username) > 0:
        if employee_data.username[0].islower():
            employee_data.username = employee_data.username[0].upper() + employee_data.username[1:]
    
    # Verificar se já existe funcionário com o mesmo username
    existing_employee = db.query(Employee).filter(
        Employee.username == employee_data.username,
        Employee.is_active == True
    ).first()
    
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um funcionário com este username"
        )
    
    # Hash da senha
    hashed_password = get_password_hash(employee_data.password)
    
    # Criar o funcionário
    employee_dict = employee_data.model_dump(exclude={"password"})
    new_employee = Employee(
        **employee_dict,
        password_hash=hashed_password
    )
    
    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar funcionário"
        )

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int, 
    employee_data: EmployeeUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """Atualizar funcionário"""
    # Garantir que o username comece com letra maiúscula, se fornecido
    if employee_data.username and len(employee_data.username) > 0:
        if employee_data.username[0].islower():
            employee_data.username = employee_data.username[0].upper() + employee_data.username[1:]
    
    # Primeiro tenta encontrar o funcionário ativo
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Atualizar campos fornecidos
    update_data = employee_data.model_dump(exclude_unset=True)
    
    # Se uma nova senha for fornecida, fazer o hash
    if 'password' in update_data and update_data['password']:
        update_data['password_hash'] = get_password_hash(update_data.pop('password'))
    
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    try:
        db.commit()
        db.refresh(employee)
        return employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar funcionário"
        )

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> None:
    """Deletar funcionário (soft delete)"""
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.is_active == True
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Soft delete
    employee.is_active = False
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover funcionário"
        )
