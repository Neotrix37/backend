# PDV System Backend 
from .core.database import Base, SessionLocal, engine, get_db

# This will make db available when importing from app
from .core import database as db

# Exporta os componentes principais
__all__ = ['Base', 'SessionLocal', 'engine', 'get_db']