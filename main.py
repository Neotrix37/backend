import os
import sys
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    from app.api.api_v1.api import api_router
    
    # Configuração inicial do FastAPI
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Backend do Sistema PDV - API para gestão de produtos, funcionários e sincronização",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # Middleware para forçar HTTPS
    if settings.ENVIRONMENT != "development":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Configurar hosts confiáveis
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "*",  # Em produção, substitua por seus domínios reais
            ".railway.app",
            "localhost",
            "127.0.0.1"
        ]
    )
    
    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware personalizado para redirecionamento HTTPS
    @app.middleware("http")
    async def force_https_redirect(request: Request, call_next):
        # Não redirecionar requisições para /docs
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            return await call_next(request)
            
        # Verificar se já é HTTPS
        if request.url.scheme == "https" or settings.ENVIRONMENT == "development":
            return await call_next(request)
            
        # Redirecionar para HTTPS
        https_url = request.url.replace(scheme="https")
        return RedirectResponse(https_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)
    
    # Incluir rotas da API
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Rota raiz
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/docs")
    
    # Rota de saúde robusta
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
    
    print("✅ Aplicação configurada com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {str(e)}")
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
    
    print("\n🚀 Iniciando servidor...")
    print(f"   Ambiente: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"   Debug: {os.getenv('DEBUG', 'False')}")
    print(f"   Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"   Porta: {os.getenv('PORT', '8000')}")
    
    uvicorn.run(
        "main:app",
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', '8000')),
        reload=os.getenv('DEBUG', 'False').lower() == 'true',
        log_level="info"
    )