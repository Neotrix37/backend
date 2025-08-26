#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
Executar: python scripts/populate_database.py
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.employee import Employee
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.inventory import Inventory
from app.models.user import User
from passlib.context import CryptContext

# Configurar contexto de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)

def create_tables():
    """Criar todas as tabelas se não existirem"""
    Base.metadata.create_all(bind=engine)

def populate_users(db: Session):
    """Popular usuários do sistema"""
    print("Verificando usuários...")
    # Upsert do usuário admin
    admin = db.query(User).filter(User.username == "Marrapaz").first()
    if admin:
        print("Atualizando usuário Marrapaz existente...")
        admin.email = "marrapaz@empresa.com"
        admin.full_name = "Usuário Marrapaz"
        admin.hashed_password = get_password_hash("842384")
        admin.role = "admin"
        admin.is_superuser = True
        admin.is_active = True
    else:
        print("Criando usuário Marrapaz...")
        admin = User(
            username="Marrapaz",
            email="marrapaz@empresa.com",
            full_name="Usuário Marrapaz",
            hashed_password=get_password_hash("842384"),
            role="admin",
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
    
    db.commit()
    return admin

def populate_categories(db: Session):
    """Popular categorias"""
    print("Verificando categorias...")
    
    # Verificar se já existem categorias
    existing_categories = db.query(Category).filter(Category.is_active == True).all()
    if existing_categories:
        print(f"✅ {len(existing_categories)} categorias já existem")
        return existing_categories
    
    print("Criando categorias...")
    
    categories_data = [
        {
            "name": "Bebidas",
            "description": "Produtos líquidos para consumo",
            "color": "#3B82F6"
        },
        {
            "name": "Alimentos",
            "description": "Produtos alimentícios em geral",
            "color": "#10B981"
        },
        {
            "name": "Limpeza",
            "description": "Produtos de limpeza e higiene",
            "color": "#F59E0B"
        },
        {
            "name": "Eletrônicos",
            "description": "Produtos eletrônicos e tecnologia",
            "color": "#8B5CF6"
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories.append(category)
    
    db.commit()
    print(f"✅ {len(categories)} categorias criadas")
    return categories

def populate_products(db: Session, categories):
    """Popular produtos"""
    print("Verificando produtos...")
    
    # Verificar se já existem produtos
    existing_products = db.query(Product).filter(Product.is_active == True).all()
    if existing_products:
        print(f"✅ {len(existing_products)} produtos já existem")
        return existing_products
    
    print("Criando produtos...")
    
    products_data = [
        {
            "name": "Coca-Cola 2L",
            "description": "Refrigerante Coca-Cola 2 litros",
            "sku": "COCA-2L",
            "barcode": "7891234567890",
            "cost_price": Decimal("4.50"),
            "sale_price": Decimal("7.90"),
            "wholesale_price": Decimal("6.50"),
            "current_stock": 50,
            "min_stock": 10,
            "max_stock": 200,
            "category_id": categories[0].id,  # Bebidas
            "is_service": False,
            "venda_por_peso": False
        },
        {
            "name": "Arroz Branco 5kg",
            "description": "Arroz branco tipo 1, 5kg",
            "sku": "ARROZ-5KG",
            "barcode": "7891234567891",
            "cost_price": Decimal("15.00"),
            "sale_price": Decimal("22.90"),
            "wholesale_price": Decimal("19.90"),
            "current_stock": 30,
            "min_stock": 5,
            "max_stock": 100,
            "category_id": categories[1].id,  # Alimentos
            "is_service": False,
            "venda_por_peso": True
        },
        {
            "name": "Detergente Líquido 500ml",
            "description": "Detergente para louças",
            "sku": "DET-500ML",
            "barcode": "7891234567892",
            "cost_price": Decimal("2.80"),
            "sale_price": Decimal("4.50"),
            "wholesale_price": Decimal("3.90"),
            "current_stock": 40,
            "min_stock": 8,
            "max_stock": 150,
            "category_id": categories[2].id,  # Limpeza
            "is_service": False,
            "venda_por_peso": False
        },
        {
            "name": "Fone de Ouvido Bluetooth",
            "description": "Fone sem fio com cancelamento de ruído",
            "sku": "FONE-BT",
            "barcode": "7891234567893",
            "cost_price": Decimal("45.00"),
            "sale_price": Decimal("89.90"),
            "wholesale_price": Decimal("75.00"),
            "current_stock": 15,
            "min_stock": 3,
            "max_stock": 50,
            "category_id": categories[3].id,  # Eletrônicos
            "is_service": False,
            "venda_por_peso": False
        }
    ]
    
    products = []
    for prod_data in products_data:
        product = Product(**prod_data)
        db.add(product)
        products.append(product)
    
    db.commit()
    print(f"✅ {len(products)} produtos criados")
    return products

def populate_employees(db: Session):
    """Popular funcionários"""
    print("Verificando funcionários...")
    
    # Verificar se já existem funcionários
    existing_employees = db.query(Employee).filter(Employee.is_active == True).all()
    if existing_employees:
        print(f"✅ {len(existing_employees)} funcionários já existem")
        return existing_employees
    
    print("Criando funcionários...")
    
    employees_data = [
        {
            "name": "João Silva",
            "email": "joao.silva@empresa.com",
            "phone": "(11) 99999-1111",
            "cpf": "123.456.789-00",
            "position": "Vendedor",
            "department": "Vendas",
            "hire_date": date(2023, 1, 15),
            "salary": Decimal("2500.00"),
            "address": "Rua das Flores, 123",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1100",
            "can_sell": True
        },
        {
            "name": "Maria Santos",
            "email": "maria.santos@empresa.com",
            "phone": "(11) 99999-2222",
            "cpf": "987.654.321-00",
            "position": "Caixa",
            "department": "Vendas",
            "hire_date": date(2023, 3, 20),
            "salary": Decimal("2200.00"),
            "address": "Av. Principal, 456",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1101",
            "can_sell": True
        },
        {
            "name": "Carlos Oliveira",
            "email": "carlos.oliveira@empresa.com",
            "phone": "(11) 99999-3333",
            "cpf": "456.789.123-00",
            "position": "Gerente",
            "department": "Administrativo",
            "hire_date": date(2022, 8, 10),
            "salary": Decimal("4500.00"),
            "address": "Rua Comercial, 789",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1102",
            "can_sell": False
        }
    ]
    
    employees = []
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.add(employee)
        employees.append(employee)
    
    db.commit()
    print(f"✅ {len(employees)} funcionários criados")
    return employees

def populate_customers(db: Session):
    """Popular clientes"""
    print("Verificando clientes...")
    
    # Verificar se já existem clientes
    existing_customers = db.query(Customer).filter(Customer.is_active == True).all()
    if existing_customers:
        print(f"✅ {len(existing_customers)} clientes já existem")
        return existing_customers
    
    print("Criando clientes...")
    
    customers_data = [
        {
            "name": "Cliente VIP 1",
            "email": "cliente1@email.com",
            "phone": "(11) 88888-1111",
            "cpf_cnpj": "111.222.333-44",
            "address": "Rua do Cliente, 111",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1200",
            "birth_date": date(1985, 5, 15),
            "notes": "Cliente fiel, sempre paga em dia",
            "is_vip": True
        },
        {
            "name": "Empresa ABC Ltda",
            "email": "contato@abc.com",
            "phone": "(11) 88888-2222",
            "cpf_cnpj": "12.345.678/0001-90",
            "address": "Av. Empresarial, 222",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1201",
            "birth_date": None,
            "notes": "Empresa cliente, compras em atacado",
            "is_vip": True
        },
        {
            "name": "Cliente Comum",
            "email": "cliente3@email.com",
            "phone": "(11) 88888-3333",
            "cpf_cnpj": "555.666.777-88",
            "address": "Rua Simples, 333",
            "city": "Maputo",
            "state": "Maputo",
            "zip_code": "1202",
            "birth_date": date(1990, 10, 20),
            "notes": "Cliente ocasional",
            "is_vip": False
        }
    ]
    
    customers = []
    for cust_data in customers_data:
        customer = Customer(**cust_data)
        db.add(customer)
        customers.append(customer)
    
    db.commit()
    print(f"✅ {len(customers)} clientes criados")
    return customers

def populate_sales(db: Session, products, employees, customers):
    """Popular vendas"""
    print("Verificando vendas...")
    
    # Verificar se já existem vendas
    existing_sales = db.query(Sale).filter(Sale.is_active == True).all()
    if existing_sales:
        print(f"✅ {len(existing_sales)} vendas já existem")
        return existing_sales
    
    print("Criando vendas...")
    
    # Venda 1: Cliente VIP compra bebidas e alimentos
    sale1 = Sale(
        sale_number="V001",
        status="completed",
        subtotal=Decimal("30.80"),
        tax_amount=Decimal("3.08"),
        discount_amount=Decimal("2.00"),
        total_amount=Decimal("31.88"),
        payment_method="credit_card",
        payment_status="paid",
        customer_id=customers[0].id,  # Cliente VIP
        employee_id=employees[0].id,  # João Silva
        notes="Venda com desconto VIP",
        is_delivery=False
    )
    db.add(sale1)
    db.flush()  # Para obter o ID da venda
    
    # Itens da venda 1
    sale1_items = [
        SaleItem(
            quantity=2,
            unit_price=Decimal("7.90"),
            discount_percent=Decimal("5.0"),
            total_price=Decimal("15.01"),
            sale_id=sale1.id,
            product_id=products[0].id  # Coca-Cola
        ),
        SaleItem(
            quantity=1,
            unit_price=Decimal("22.90"),
            discount_percent=Decimal("0.0"),
            total_price=Decimal("22.90"),
            sale_id=sale1.id,
            product_id=products[1].id  # Arroz
        )
    ]
    
    for item in sale1_items:
        db.add(item)
    
    # Venda 2: Empresa compra produtos de limpeza
    sale2 = Sale(
        sale_number="V002",
        status="completed",
        subtotal=Decimal("18.00"),
        tax_amount=Decimal("1.80"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("19.80"),
        payment_method="bank_transfer",
        payment_status="paid",
        customer_id=customers[1].id,  # Empresa ABC
        employee_id=employees[1].id,  # Maria Santos
        notes="Compra para estoque da empresa",
        is_delivery=True,
        delivery_address="Av. Empresarial, 222 - Maputo"
    )
    db.add(sale2)
    db.flush()
    
    # Itens da venda 2
    sale2_items = [
        SaleItem(
            quantity=4,
            unit_price=Decimal("4.50"),
            discount_percent=Decimal("0.0"),
            total_price=Decimal("18.00"),
            sale_id=sale2.id,
            product_id=products[2].id  # Detergente
        )
    ]
    
    for item in sale2_items:
        db.add(item)
    
    db.commit()
    print(f"✅ 2 vendas criadas com {len(sale1_items) + len(sale2_items)} itens")
    
    return [sale1, sale2]

def populate_inventory_movements(db: Session, products):
    """Popular movimentações de inventário"""
    print("Verificando movimentações de inventário...")
    
    # Verificar se já existem movimentações
    existing_movements = db.query(Inventory).filter(Inventory.is_active == True).all()
    if existing_movements:
        print(f"✅ {len(existing_movements)} movimentações de inventário já existem")
        return
    
    print("Criando movimentações de inventário...")
    
    # Movimentação inicial de compra para cada produto
    for product in products:
        movement = Inventory(
            movement_type="purchase",
            quantity=product.current_stock,
            previous_stock=0,
            new_stock=product.current_stock,
            reference_id="COMPRA_INICIAL",
            reference_type="initial_stock",
            notes="Estoque inicial do sistema",
            product_id=product.id
        )
        db.add(movement)
    
    db.commit()
    print(f"✅ {len(products)} movimentações de inventário criadas")

def main():
    """Função principal"""
    print("🚀 Iniciando população do banco de dados...")
    
    # Criar tabelas se não existirem
    create_tables()
    
    # Obter sessão do banco
    db = SessionLocal()
    
    try:
        # Popular dados na ordem correta (respeitando foreign keys)
        users = populate_users(db)
        categories = populate_categories(db)
        products = populate_products(db, categories)
        employees = populate_employees(db)
        customers = populate_customers(db)
        sales = populate_sales(db, products, employees, customers)
        populate_inventory_movements(db, products)
        
        print("\n🎉 Banco de dados populado com sucesso!")
        print(f"📊 Resumo:")
        print(f"   - Usuários: {len([users])}")
        print(f"   - Categorias: {len(categories)}")
        print(f"   - Produtos: {len(products)}")
        print(f"   - Funcionários: {len(employees)}")
        print(f"   - Clientes: {len(customers)}")
        print(f"   - Vendas: {len(sales)}")
        
        print(f"\n🔐 Credenciais de acesso:")
        print(f"   - Username: Marrapaz")
        print(f"   - Senha: 842384")
        print(f"   - Role: Admin")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
