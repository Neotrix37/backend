from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # Configurações da Aplicação
    APP_NAME: str = "PDV System Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Validação da URL do banco de dados
    if not DATABASE_URL:
        raise ValueError("A variável de ambiente DATABASE_URL não está definida")
        
    # Garante que a URL do banco de dados use o formato correto para SQLAlchemy
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua-chave-secreta-muito-segura-aqui-2024")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configurações de CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://backend-production-046c.up.railway.app",
        "https://*.up.railway.app"
    ]
    
    class Config:
        case_sensitive = True

# Instância global das configurações
try:
    settings = Settings()
except ValueError as e:
    print(f"Erro de configuração: {e}")
    raise