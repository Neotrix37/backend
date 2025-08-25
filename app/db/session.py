"""
Configuração da sessão do banco de dados SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from ..core.config import settings

# Criar engine do SQLAlchemy
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Criar fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db():
    ""
    Fornece uma sessão do banco de dados.
    
    Uso:
    ```
    db = next(get_db())
    ```
    """
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
