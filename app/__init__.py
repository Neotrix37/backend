"""
PDV System Backend - Módulo principal da aplicação
"""

# Importações principais
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para o Sistema PDV",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar rotas da API
try:
    from .api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Rota de health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": settings.PROJECT_NAME}
        
except ImportError as e:
    print(f"Aviso: Não foi possível carregar as rotas da API: {e}")

# Importar modelos para garantir que o SQLAlchemy os reconheça
try:
    from . import models  # noqa: F401
except ImportError as e:
    print(f"Aviso: Não foi possível importar os modelos: {e}")