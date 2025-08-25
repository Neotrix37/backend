from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Configurações da Aplicação
    APP_NAME: str = "PDV System Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/pdv_system")
    # Garante que a URL do banco de dados use o formato correto para SQLAlchemy
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Configurações de Segurança
    SECRET_KEY: str = "sua-chave-secreta-muito-segura-aqui-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações de CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Adicione aqui os domínios de produção
        "https://seu-frontend-dominio.com",
        "https://www.seu-frontend-dominio.com"
    ]
    
    # Configurações de Email (futuro)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instância global das configurações
settings = Settings()