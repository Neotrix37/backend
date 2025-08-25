from fastapi import APIRouter
from .endpoints import auth, products, categories, sales, customers, employees, inventory, users

api_router = APIRouter()

# Incluir todas as rotas da API
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
