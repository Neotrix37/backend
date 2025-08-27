# Endpoints da API v1

from .auth import router as auth_router
from .cart import router as cart_router
from .categories import router as categories_router
from .customers import router as customers_router
from .employees import router as employees_router
from .inventory import router as inventory_router
from .products import router as products_router
from .sales import router as sales_router
from .users import router as users_router

__all__ = [
    'auth_router',
    'cart_router',
    'categories_router',
    'customers_router',
    'employees_router',
    'inventory_router',
    'products_router',
    'sales_router',
    'users_router',
]
