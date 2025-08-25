from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from typing import Optional, Callable, Awaitable

from app.core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança HTTP"""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Headers de segurança
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }
        
        # Adicionar headers à resposta
        for header, value in security_headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        return response

def setup_middlewares(app: ASGIApp) -> None:
    """Configura todos os middlewares da aplicação"""
    
    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"]
    )
    
    # Middleware de headers de segurança
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Em produção, forçar HTTPS
    if not settings.DEBUG:
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Middleware de hosts confiáveis
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
