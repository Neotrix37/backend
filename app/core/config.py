import os
from pydantic import field_validator, ConfigDict
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
    ALLOWED_ORIGINS: str = "*"
    
    # Configurações do Servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configurações de Segurança Adicionais
    SECURE_COOKIES: bool = not DEBUG
    
    # Configurações de Rate Limiting
    RATE_LIMIT: str = "100/minute"
    
    model_config = ConfigDict(
        extra="ignore",  # Ignora campos extras que não estão definidos
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "":
            return []
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância de configurações em cache"""
    return Settings()

# Instância global das configurações
settings = get_settings()