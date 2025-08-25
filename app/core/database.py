from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from app.core.config import settings

# URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)

# Cria o Base
Base = declarative_base()

# Engine e sessão
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependência FastAPI para obter e liberar sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()