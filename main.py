from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI sem redirecionamentos automáticos
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend do Sistema PDV",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração CORS
origins = [
    "https://vuchada-cyan.vercel.app",
    "http://localhost:3000",  # Para desenvolvimento local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "details": str(exc) if settings.ENVIRONMENT == "development" else None
        }
    )

# Request Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

try:
    # Tenta importar e incluir as rotas da API
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    logger.info("✅ Rotas da API carregadas com sucesso!")
except Exception as e:
    logger.error(f"⚠️ Aviso ao carregar rotas da API: {e}", exc_info=True)

# Rota raiz simplificada
@app.get("/")
async def root():
    return {
        "message": "Sistema PDV Backend",
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

# Rota de saúde simplificada
@app.get("/health")
async def health_check():
    try:
        # Adicione verificações de saúde aqui (banco de dados, etc.)
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "timestamp": "2025-08-27T04:30:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )

# Para execução local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, log_level="info")