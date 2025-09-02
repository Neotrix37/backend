from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Type, TypeVar, Generic
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.user import User
from app.models.employee import Employee

from app.schemas.sync import SyncResponse, SyncQuery
from app.schemas.product_sync import ProductSyncResponse
from app.schemas.category import CategoryCreate
from app.schemas.customer_sync import CustomerSyncResponse
from app.schemas.sale_sync import SaleSyncResponse
from app.schemas.user_sync import UserSyncResponse
from app.schemas.employee_sync import EmployeeSyncResponse
from app.schemas.report_sync import FinancialReportSyncResponse, ReportSyncResponse, ReportSyncRequest

router = APIRouter()

T = TypeVar('T')

def sync_table(db: Session, model: Type[T], records: List[T]) -> SyncResponse[T]:
    """Função genérica para sincronizar registros de qualquer tabela"""
    synced = []
    conflicts = []
    
    for record in records:
        db_record = db.query(model).filter(model.id == record.id).first()
        
        if not db_record:
            # Novo registro
            db_record = model(**record.dict())
            db.add(db_record)
            synced.append(record)
        else:
            # Registro existente - verificar timestamp
            if record.last_updated > db_record.last_updated:
                # Atualizar registro no servidor
                for key, value in record.dict().items():
                    setattr(db_record, key, value)
                synced.append(record)
            else:
                # Conflito - registro do servidor é mais recente
                conflicts.append(record)
    
    db.commit()
    return SyncResponse(synced_records=synced, conflicts=conflicts)

@router.get("/products", response_model=SyncResponse[ProductSyncResponse])
async def get_products_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    products = db.query(Product).filter(Product.last_updated > last_sync).all()
    return SyncResponse(server_updated=products)

@router.post("/products", response_model=SyncResponse[ProductSyncResponse])
async def sync_products(
    products: List[ProductSyncResponse],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, Product, products)

@router.get("/categories", response_model=SyncResponse[CategoryCreate])
async def get_categories_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    categories = db.query(Category).filter(Category.last_updated > last_sync).all()
    return SyncResponse(server_updated=categories)

@router.post("/categories", response_model=SyncResponse[CategoryCreate])
async def sync_categories(
    categories: List[CategoryCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, Category, categories)

@router.get("/customers", response_model=SyncResponse[CustomerSyncResponse])
async def get_customers_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customers = db.query(Customer).filter(Customer.last_updated > last_sync).all()
    return SyncResponse(server_updated=customers)

@router.post("/customers", response_model=SyncResponse[CustomerSyncResponse])
async def sync_customers(
    customers: List[CustomerSyncResponse],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, Customer, customers)

@router.get("/sales", response_model=SyncResponse[SaleSyncResponse])
async def get_sales_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from sqlalchemy.orm import joinedload
    
    sales = db.query(Sale).options(joinedload(Sale.items), joinedload(Sale.user)).filter(Sale.last_updated > last_sync).all()
    
    # Convert sale items to properly handle NULL values
    converted_sales = []
    for sale in sales:
        sale_dict = sale.__dict__.copy()
        if hasattr(sale, 'items'):
            sale_dict['items'] = [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": float(item.quantity) if item.quantity else 0.0,
                    "unit_price": float(item.unit_price) if item.unit_price else 0.0,
                    "total_price": float(item.total_price) if item.total_price else 0.0,
                    "is_weight_sale": bool(getattr(item, 'is_weight_sale', False)),
                    "weight_in_kg": float(getattr(item, 'weight_in_kg', 0)) if getattr(item, 'weight_in_kg', None) else None,
                    "custom_price": float(getattr(item, 'custom_price', 0)) if getattr(item, 'custom_price', None) else None,
                    "created_at": item.created_at
                } for item in sale.items
            ]
        # Adicionar informações do usuário
        if hasattr(sale, 'user') and sale.user:
            sale_dict['user_id'] = sale.user.id
            sale_dict['user_name'] = sale.user.full_name
        else:
            sale_dict['user_id'] = None
            sale_dict['user_name'] = "Usuário Desconhecido"
        converted_sales.append(sale_dict)
    
    return SyncResponse(server_updated=converted_sales)

@router.post("/sales", response_model=SyncResponse[SaleSyncResponse])
async def sync_sales(
    sales: List[SaleSyncResponse],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, Sale, sales)

@router.get("/users", response_model=SyncResponse[UserSyncResponse])
async def get_users_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    users = db.query(User).filter(User.last_updated > last_sync).all()
    return SyncResponse(server_updated=users)

@router.post("/users", response_model=SyncResponse[UserSyncResponse])
async def sync_users(
    users: List[UserSyncResponse],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, User, users)

@router.get("/employees", response_model=SyncResponse[EmployeeSyncResponse])
async def get_employees_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    employees = db.query(Employee).filter(Employee.last_updated > last_sync).all()
    return SyncResponse(server_updated=employees)

@router.post("/employees", response_model=SyncResponse[EmployeeSyncResponse])
async def sync_employees(
    employees: List[EmployeeSyncResponse],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sync_table(db, Employee, employees)

@router.get("/reports", response_model=ReportSyncResponse)
async def get_reports_for_sync(
    last_sync: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para obter relatórios financeiros atualizados desde a última sincronização"""
    # Como relatórios são gerados dinamicamente, retornamos uma lista vazia
    # pois relatórios não são armazenados no banco, são gerados sob demanda
    return ReportSyncResponse(
        synced_reports=[],
        conflicts=[],
        server_updated=[]
    )

@router.post("/reports", response_model=ReportSyncResponse)
async def sync_reports(
    report_request: ReportSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint para sincronizar relatórios financeiros (principalmente para histórico)"""
    # Relatórios são principalmente para consulta, então sincronização é simples
    synced_reports = []
    conflicts = []
    
    for report in report_request.reports:
        # Verificar se já existe um relatório com mesmo período e tipo
        # Como relatórios são gerados dinamicamente, geralmente não há conflitos
        synced_reports.append(report)
    
    return ReportSyncResponse(
        synced_reports=synced_reports,
        conflicts=conflicts,
        server_updated=[]
    )