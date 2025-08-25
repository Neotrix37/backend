from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações da Aplicação
    APP_NAME: str = "PDV System Backend"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Configurações do Banco de Dados
    DATABASE_URL: str
    DATABASE_INTERNAL_URL: Optional[str] = None
    
    # Configurações de Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Configurações de CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Configurações de Email (opcional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Configurações do Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == 'ALLOWED_ORIGINS':
                if not raw_val:
                    return []
                if isinstance(raw_val, str):
                    if raw_val.strip() == '"*"' or raw_val.strip() == "'*'":
                        return ["*"]
                    return [origin.strip() for origin in raw_val.split(",") if origin.strip()]
            return cls.json_loads(raw_val)  # type: ignore

# Instância global das configurações
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()