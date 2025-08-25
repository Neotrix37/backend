import os
import sys
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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
    
    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    
    # Rota de saúde simplificada
    @app.get("/health", status_code=200)
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    
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