from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações básicas
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Configurações da Aplicação
    APP_NAME: str = "PDV System Backend"
    API_V1_STR: str = "/api/v1"
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = ""
    DATABASE_INTERNAL_URL: Optional[str] = ""
    
    # Configurações de Segurança
    SECRET_KEY: str = "dummy-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Configurações de CORS e HTTPS
    ALLOWED_ORIGINS: str = "*"
    FORCE_HTTPS: bool = False  # Desativado para permitir conexões HTTP
    
    @property
    def trusted_hosts(self) -> List[str]:
        if self.ENVIRONMENT == "development":
            return ["*", "localhost", "127.0.0.1"]
        return [
            ".railway.app",
            "backend-production-f01c.up.railway.app",
            "localhost",
            "127.0.0.1"
        ]
    
    # Configurações de Email (opcionais com valores padrão)
    SMTP_HOST: str = ""
    SMTP_PORT: str = "587"  # Mantendo como string para compatibilidade
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Configurações do Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Método para converter a string de origens em lista
    @property
    def allowed_origins_list(self) -> List[str]:
        if self.ENVIRONMENT == "development":
            return ["*"]
            
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "":
            return []
            
        origins = [
            "https://*.railway.app",
            "http://*.railway.app",
            "https://backend-production-f01c.up.railway.app",
            "http://backend-production-f01c.up.railway.app"
        ]
        
        # Adiciona origens personalizadas se especificadas
        if self.ALLOWED_ORIGINS.strip() != "*":
            origins.extend([origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()])
            
        return list(set(origins))  # Remove duplicatas
    
    # Validador para garantir que PORT seja um inteiro
    @field_validator('PORT', mode='before')
    @classmethod
    def validate_port(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return 8000
        return v or 8000
    
    # Validador para SMTP_PORT
    @field_validator('SMTP_PORT', mode='before')
    @classmethod
    def validate_smtp_port(cls, v):
        if v is None or v == '':
            return "587"
        # Garante que o valor seja tratado como string
        return str(v)
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"

# Instância global das configurações
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()