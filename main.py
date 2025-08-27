from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Cria a aplicação FastAPI sem redirecionamentos automáticos
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend do Sistema PDV",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração CORS simplificada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens temporariamente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    # Tenta importar e incluir as rotas da API
    from app.api.api_v1.api import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    print("✅ Rotas da API carregadas com sucesso!")
except Exception as e:
    print(f"⚠️ Aviso ao carregar rotas da API: {e}")

# Rota raiz simplificada
@app.get("/")
async def root():
    return {
        "message": "Sistema PDV Backend",
        "status": "online"
    }

# Rota de saúde simplificada
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Para execução local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")