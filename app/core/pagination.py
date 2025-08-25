from typing import TypeVar, Generic, List, Optional, Any, Type
from pydantic import BaseModel
from fastapi import Query as FastAPIQuery
from fastapi_pagination import Page as BasePage, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import Select
from sqlalchemy.orm import Session

# Type variable for Pydantic models
T = TypeVar('T')

class Page(BasePage[T], Generic[T]):
    """Página de resultados com metadados de paginação"""
    class Config:
        json_encoders = {
            'decimal.Decimal': str  # Converte Decimal para string no JSON
        }

def paginate(
    db: Session,
    query: Select,
    page: int = 1,
    size: int = 20
) -> Page[Any]:
    """
    Executa uma consulta paginada no banco de dados
    
    Args:
        db: Sessão do banco de dados
        query: Consulta SQLAlchemy Select
        page: Número da página (1-based)
        size: Itens por página
        
    Returns:
        Page[T]: Página de resultados com metadados de paginação
    """
    # Ajustar valores de paginação
    page = max(1, page)
    size = max(1, min(size, 100))  # Limitar a 100 itens por página
    
    # Executar a consulta paginada
    params = Params(page=page, size=size)
    return sqlalchemy_paginate(query, params=params, session=db)
