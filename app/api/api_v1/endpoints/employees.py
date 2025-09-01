from fastapi import APIRouter, HTTPException, status, Depends, Security
from typing import List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.models.employee import Employee, EmployeeRole
from app.models.user import User
from app.core.database import get_db
from app.core.security import (
    get_password_hash, 
    get_current_active_user,
    is_admin,
    is_manager_or_admin,
    can_manage_employees
)

router = APIRouter()

def check_employee_permission(
    current_user: User = Depends(get_current_active_user),
    employee: Employee = None
):
    """
    Verifica se o usuário tem permissão para acessar/modificar o funcionário
    """
    # Admin pode acessar tudo
    if current_user.role == EmployeeRole.ADMIN:
        return True
        
    # Gerente só pode acessar funcionários comuns e caixas
    if current_user.role == EmployeeRole.MANAGER:
        if employee and employee.role in [EmployeeRole.ADMIN, EmployeeRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso"
            )
        return True
        
    # Outras roles não têm permissão
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado. Permissão insuficiente"
    )

@router.get("/", response_model=List[EmployeeResponse], 
          dependencies=[Depends(can_manage_employees)])
async def get_employees(
    show_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Listar funcionários.
    Parâmetros:
    - show_inactive: Se True, inclui funcionários inativos (apenas admin)
    """
    query = db.query(Employee)
    
    # Se não for admin, forçar mostrar apenas ativos
    if current_user.role != EmployeeRole.ADMIN:
        show_inactive = False
        query = query.filter(Employee.is_active == True)
    # Se for admin e não pediu inativos, filtrar apenas ativos
    elif not show_inactive:
        query = query.filter(Employee.is_active == True)
    
    # Filtro adicional para gerentes (só veem caixas e visualizadores)
    if current_user.role == EmployeeRole.MANAGER:
        query = query.filter(Employee.role.in_([EmployeeRole.CASHIER, EmployeeRole.VIEWER]))
    
    return query.all()

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obter funcionário por ID.
    Apenas administradores e gerentes podem acessar.
    """
    # Busca o funcionário mesmo se estiver inativo
    employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Verifica permissão para acessar o funcionário
    check_employee_permission(current_user, employee)
    
    return employee

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Criar novo funcionário.
    Apenas administradores e gerentes podem acessar.
    """
    # Verifica permissão
    check_employee_permission(current_user)
    
    # Verifica se a role é válida para o usuário atual
    if (current_user.role == EmployeeRole.MANAGER and 
        employee_data.role in [EmployeeRole.ADMIN, EmployeeRole.MANAGER]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar um usuário com este cargo"
        )
    
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
    
    # Criar novo funcionário
    db_employee = Employee(
        **employee_data.dict(exclude={"password"}),
        password_hash=get_password_hash(employee_data.password)
    )
    
    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Atualizar funcionário.
    Apenas administradores e gerentes podem acessar.
    """
    # Busca o funcionário mesmo se estiver inativo
    db_employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Verifica permissão para modificar o funcionário
    check_employee_permission(current_user, db_employee)
    
    # Verifica se está tentando modificar a role
    if employee_data.role and employee_data.role != db_employee.role:
        if (current_user.role == EmployeeRole.MANAGER and 
            employee_data.role in [EmployeeRole.ADMIN, EmployeeRole.MANAGER]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para alterar para este cargo"
            )
    
    # Atualizar campos
    update_data = employee_data.dict(exclude_unset=True, exclude={"password"})
    
    # Atualizar senha se fornecida
    if employee_data.password:
        update_data["password_hash"] = get_password_hash(employee_data.password)
    
    for field, value in update_data.items():
        setattr(db_employee, field, value)
    
    try:
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar funcionário"
        )

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Desativar funcionário (soft delete).
    Apenas administradores e gerentes podem acessar.
    """
    # Busca o funcionário mesmo se já estiver inativo
    db_employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Verifica se o funcionário já está inativo
    if not db_employee.is_active:
        return  # Já está inativo, retorna sucesso sem fazer nada
    
    # Verifica permissão para desativar o funcionário
    check_employee_permission(current_user, db_employee)
    
    # Não permitir desativar a si mesmo
    if db_employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar sua própria conta"
        )
    
    # Soft delete
    db_employee.is_active = False
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao desativar funcionário"
        )
