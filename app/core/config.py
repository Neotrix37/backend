import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações básicas
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Configurações da Aplicação
    PROJECT_NAME: str = "PDV System Backend"
    API_V1_STR: str = "/api/v1"
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DATABASE_INTERNAL_URL: str = os.getenv("DATABASE_INTERNAL_URL", "")
    
    # Configurações de Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutos
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # 7 dias
    
    # Configurações de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Configurações do Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configurações de Segurança Adicionais
    SECURE_COOKIES: bool = not DEBUG
    
    # Configurações de Rate Limiting
    RATE_LIMIT: str = "100/minute"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância de configurações em cache"""
    return Settings()

# Instância global das configurações
settings = get_settings()