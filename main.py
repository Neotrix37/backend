import os
import sys
from fastapi import FastAPI, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização da aplicação
    print(" Iniciando aplicação...")
    yield
    # Encerramento da aplicação
    print(" Encerrando aplicação...")

try:
    from app.core.config import settings
    from app.api.api_v1.api import api_router
    from app.db.session import engine, Base
    from app.core.middleware import SecurityHeadersMiddleware
    
    # Configuração inicial do FastAPI
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Backend do Sistema PDV - API para gestão de produtos, funcionários e sincronização",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"]
    )
    
    # Middleware de headers de segurança
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Forçar HTTPS em produção
    if not settings.DEBUG:
        app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Em produção, substituir por domínios permitidos
        )
    
    # Incluir rotas da API
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Rota raiz
    @app.get("/")
    async def root():
        return {
            "message": "Bem-vindo ao Sistema PDV Backend",
            "version": "1.0.0",
            "status": "online",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs"
        }
    
    # Rota de saúde
    @app.get("/health", status_code=200, tags=["health"])
    async def health_check():
        try:
            # Verificar conexão com o banco de dados
            from sqlalchemy import text
            from app.db.session import SessionLocal
            
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            
            return {
                "status": "healthy",
                "service": settings.APP_NAME,
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "unhealthy",
                    "error": str(e),
                    "service": settings.APP_NAME,
                    "environment": settings.ENVIRONMENT,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    print(" Aplicação configurada com sucesso!")
    
except ImportError as e:
    print(f" Erro ao importar módulos: {str(e)}")
    print("Verifique se todos os módulos necessários estão instalados corretamente.")
    print("Execute: pip install -r requirements.txt")
    
    # Criar uma aplicação mínima para exibir erros
    app = FastAPI()
    
    @app.get("/")
    async def error_root():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na inicialização da aplicação: {str(e)}"
        )

# Ponto de entrada para o Gunicorn/Uvicorn
if __name__ == "__main__":
    import uvicorn
    
    print("\n Iniciando servidor...")
    print(f"   Ambiente: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"   Debug: {os.getenv('DEBUG', 'False')}")
    print(f"   Acesse: http://{settings.HOST}:{settings.PORT}")
    print(f"   Documentação: http://{settings.HOST}:{settings.PORT}/docs\n")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="debug" if settings.DEBUG else "info"
    )