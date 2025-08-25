from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

load_dotenv()

# Obter a URL do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Criar sessão local
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Classe base para os modelos
Base = declarative_base()

def get_db():
    """Obter uma instância do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar o banco de dados"""
    import app.models  # Importar todos os modelos
    Base.metadata.create_all(bind=engine)
