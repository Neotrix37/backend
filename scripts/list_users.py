#!/usr/bin/env python3
"""
Script para listar todos os usuários no banco de dados
Executar: python scripts/list_users.py
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

def list_users():
    """Lista todos os usuários no banco de dados"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("Nenhum usuário encontrado no banco de dados.")
            return
            
        print("\n=== USUÁRIOS CADASTRADOS ===")
        for user in users:
            print(f"\nID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Nome: {user.full_name}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Superusuário: {'Sim' if user.is_superuser else 'Não'}")
            print(f"Ativo: {'Sim' if user.is_active else 'Não'}")
            print(f"Criado em: {user.created_at}")
            
    except Exception as e:
        print(f"Erro ao listar usuários: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Buscando usuários no banco de dados...")
    list_users()
