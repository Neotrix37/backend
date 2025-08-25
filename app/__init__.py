"""
PDV System Backend - Módulo principal da aplicação
"""

# Importações principais
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

# Criar aplicação FastAPI
def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API para o Sistema PDV",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configurar CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Incluir rotas da API
    from .api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Rota de health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app

# Inicializar a aplicação
app = create_app()

# Importar modelos para garantir que o SQLAlchemy os reconheça
from . import models  # noqa: F401, E402