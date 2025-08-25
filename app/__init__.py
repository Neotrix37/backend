# PDV System Backend 
from .models.base import Base
from .core.database import engine, SessionLocal

# This will make db available when importing from app
from .core import database as db

# This will be imported by FastAPI
__all__ = ['Base', 'SessionLocal', 'engine']