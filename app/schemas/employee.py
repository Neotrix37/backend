from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from decimal import Decimal
from enum import Enum
from .base import BaseResponse, BaseCreate, BaseUpdate

class EmployeeRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    VIEWER = "viewer"

class EmployeeCreate(BaseCreate):
    full_name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: EmployeeRole = Field(default=EmployeeRole.CASHIER)
    salary: Optional[Decimal] = Field(None, ge=0)
    
    @validator('username')
    def username_must_be_lowercase(cls, v):
        if v.lower() != v:
            raise ValueError('O nome de usuário deve estar em minúsculas')
        return v

class EmployeeUpdate(BaseUpdate):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[EmployeeRole] = None
    salary: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    @validator('username', pre=True, always=True)
    def username_must_be_lowercase(cls, v):
        if v and v.lower() != v:
            raise ValueError('O nome de usuário deve estar em minúsculas')
        return v

class EmployeeResponse(BaseResponse):
    full_name: str
    username: str
    role: EmployeeRole
    salary: Optional[Decimal] = None
    is_active: bool = True
    
    # Permissões baseadas no papel
    can_manage_products: bool = False
    can_manage_categories: bool = False
    can_manage_sales: bool = False
    can_manage_customers: bool = False
    can_manage_employees: bool = False
    can_manage_inventory: bool = False
    can_view_reports: bool = False
    can_manage_expenses: bool = False
    can_close_register: bool = False
    can_manage_system_settings: bool = False
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(round(float(v), 2)) if v is not None else None
        }
    
    @classmethod
    def from_orm(cls, obj):
        # Cria o objeto base
        employee = super().from_orm(obj)
        
        # Define as permissões baseadas no papel do funcionário
        if employee.role == EmployeeRole.ADMIN:
            employee.can_manage_products = True
            employee.can_manage_categories = True
            employee.can_manage_sales = True
            employee.can_manage_customers = True
            employee.can_manage_employees = True
            employee.can_manage_inventory = True
            employee.can_view_reports = True
            employee.can_manage_expenses = True
            employee.can_close_register = True
            employee.can_manage_system_settings = True
            
        elif employee.role == EmployeeRole.MANAGER:
            employee.can_manage_products = True
            employee.can_manage_categories = True
            employee.can_manage_sales = True
            employee.can_manage_customers = True
            employee.can_manage_employees = True  # Mas com restrições adicionais
            employee.can_manage_inventory = True
            employee.can_view_reports = True
            employee.can_manage_expenses = True
            employee.can_close_register = True
            employee.can_manage_system_settings = False
            
        elif employee.role == EmployeeRole.CASHIER:
            employee.can_manage_products = False
            employee.can_manage_categories = False
            employee.can_manage_sales = False  # Pode criar vendas, mas não gerenciar todas
            employee.can_manage_customers = False
            employee.can_manage_employees = False
            employee.can_manage_inventory = False
            employee.can_view_reports = False
            employee.can_manage_expenses = False
            employee.can_close_register = True  # Pode fechar o próprio caixa
            employee.can_manage_system_settings = False
            
        elif employee.role == EmployeeRole.VIEWER:
            employee.can_manage_products = False
            employee.can_manage_categories = False
            employee.can_manage_sales = False
            employee.can_manage_customers = False
            employee.can_manage_employees = False
            employee.can_manage_inventory = False
            employee.can_view_reports = True   # Apenas visualização
            employee.can_manage_expenses = False
            employee.can_close_register = False
            employee.can_manage_system_settings = False
        
        return employee
