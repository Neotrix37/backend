import os
import sys
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar a aplicação do módulo app
from app import app

# Configurações de CORS
origins = ["*"]

# Adicionar middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota raiz
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo ao PDV System Backend",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Rota de saúde
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Servidor está rodando"}

# Ponto de entrada para execução direta
if __name__ == "__main__":
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Iniciar o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        workers=4,
        log_level="info"
    )