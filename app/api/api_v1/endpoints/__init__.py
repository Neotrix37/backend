"""
Endpoints da API v1
"""

# Importar todos os roteadores de endpoints
from . import (
    auth,
    products,
    categories,
    sales,
    customers,
    employees,
    inventory,
    users
)

# Exportar todos os roteadores
__all__ = [
    'auth',
    'products',
    'categories',
    'sales',
    'customers',
    'employees',
    'inventory',
    'users'
]
