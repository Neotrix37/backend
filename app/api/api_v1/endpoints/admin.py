from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import subprocess
from decimal import Decimal

from app.core.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User, UserRole
from app.core.security import get_current_active_user, get_password_hash
from app.core.config import settings

router = APIRouter()

def reset_database():
    """Reseta o banco de dados para o estado inicial"""
    try:
        # Remove todas as tabelas
        Base.metadata.drop_all(bind=engine)
        
        # Cria todas as tabelas novamente
        Base.metadata.create_all(bind=engine)
        
        # Executa as migrações do Alembic
        alembic_cmd = ["alembic", "upgrade", "head"]
        subprocess.run(alembic_cmd, check=True)
        
        # Cria um usuário administrador padrão
        db = SessionLocal()
        try:
            admin_user = User(
                username="Marrapaz",
                email="neotrixtecnologias37@gmail.com",
                hashed_password=get_password_hash("842384"),
                full_name="Neotrix Tecnologias",
                role=UserRole.ADMIN,
                is_superuser=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
        return {"message": "Banco de dados resetado com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao resetar o banco de dados: {str(e)}"
        )

@router.post("/reset-database", status_code=status.HTTP_200_OK)
def admin_reset_database(
    current_user: User = Depends(get_current_active_user)
):
    """
    Reseta o banco de dados para o estado inicial (apenas para administradores)
    
    **Atenção:** Esta operação é destrutiva e irá apagar todos os dados do banco!
    """
    # Verifica se o usuário atual é administrador
    if not current_user.is_superuser and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem executar esta operação"
        )
    
    # Verifica se estamos em ambiente de desenvolvimento
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operação só é permitida em ambiente de desenvolvimento"
        )
    
    return reset_database()
