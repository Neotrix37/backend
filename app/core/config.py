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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutos
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7    # 7 dias
    
    # Configurações de CORS
    ALLOWED_ORIGINS: str = "*"
    
    # Configurações de Email (opcionais com valores padrão)
    SMTP_HOST: str = ""
    SMTP_PORT: str = "587"  # Mantendo como string para compatibilidade
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Configurações do Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configurações de Segurança Adicionais
    SECURE_COOKIES: bool = not DEBUG
    SESSION_COOKIE_NAME: str = "pdv_session"
    CSRF_COOKIE_NAME: str = "pdv_csrf"
    
    # Configurações de Rate Limiting
    RATE_LIMIT: str = "100/minute"
    
    # Método para converter a string de origens em lista
    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "":
            return []
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    # Validador para garantir que PORT seja um inteiro
    @field_validator('PORT', mode='before')
    @classmethod
    def validate_port(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("PORT deve ser um número inteiro")
        return v
    
    # Validador para garantir que as URLs de banco de dados estejam configuradas
    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            # Se não estiver configurado, tenta pegar do DATABASE_INTERNAL_URL
            # Isso é útil para ambientes como o Railway que usam variáveis diferentes
            internal_url = os.getenv('DATABASE_INTERNAL_URL')
            if internal_url:
                return internal_url
            
            # Se estiver em desenvolvimento, usa SQLite local
            if os.getenv('ENVIRONMENT', 'production') == 'development':
                return 'sqlite:///./pdv_system.db'
                
            raise ValueError("DATABASE_URL não configurado")
        return v
    
    # Validador para garantir que a chave secreta não seja a padrão em produção
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v, values):
        if v == "dummy-secret-key-change-in-production" and values.get('ENVIRONMENT') != 'development':
            raise ValueError("SECRET_KEY não pode ser o valor padrão em produção")
        return v

# Instância global das configurações
@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()