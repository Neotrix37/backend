from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
from sqlalchemy.orm import Session
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee
from app.core.database import get_db

router = APIRouter()

@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)) -> Any:
    """Listar todos os funcionários"""
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int, db: Session = Depends(get_db)) -> Any:
    """Obter funcionário por ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.is_active == True).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    return employee

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)) -> Any:
    """Criar novo funcionário"""
    # Verificar se já existe funcionário com o mesmo CPF
    existing_employee = db.query(Employee).filter(
        Employee.cpf == employee_data.cpf,
        Employee.is_active == True
    ).first()
    
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um funcionário com este CPF"
        )
    
    new_employee = Employee(**employee_data.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: int, employee_data: EmployeeUpdate, db: Session = Depends(get_db)) -> Any:
    """Atualizar funcionário existente"""
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.is_active == True).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Verificar se o novo CPF já existe em outro funcionário
    if employee_data.cpf:
        existing_employee = db.query(Employee).filter(
            Employee.cpf == employee_data.cpf,
            Employee.id != employee_id,
            Employee.is_active == True
        ).first()
        
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um funcionário com este CPF"
            )
    
    # Atualizar campos
    for field, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Deletar funcionário (soft delete)"""
    employee = db.query(Employee).filter(Employee.id == employee_id, Employee.is_active == True).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Soft delete
    employee.is_active = False
    db.commit()
