#!/usr/bin/env python3
"""
Script para migrar vendas existentes associando-as a usuários.
Este script atribui um usuário padrão (admin) às vendas que não têm user_id.
"""

import sys
import os

# Adicionar o diretório raiz ao path para importar módulos do app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.sale import Sale
from app.models.user import User

def migrate_sales_users():
    """Atribui um usuário padrão às vendas sem user_id"""
    db = SessionLocal()
    
    try:
        # Buscar o usuário admin (ou criar se não existir)
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("Usuário admin não encontrado. Criando usuário admin...")
            admin_user = User(
                username="admin",
                full_name="Administrador",
                email="admin@example.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password = "secret"
                role="admin",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Usuário admin criado com ID: {admin_user.id}")
        
        # Contar vendas sem user_id
        sales_without_user = db.query(Sale).filter(Sale.user_id == None).count()
        print(f"Vendas sem usuário: {sales_without_user}")
        
        if sales_without_user == 0:
            print("Nenhuma venda precisa de migração!")
            return
        
        # Atualizar vendas sem user_id
        result = db.query(Sale).filter(Sale.user_id == None).update(
            {Sale.user_id: admin_user.id}, 
            synchronize_session=False
        )
        
        db.commit()
        
        print(f"{result} vendas atualizadas com user_id do admin")
        print(f"Usuário atribuído: {admin_user.full_name} (ID: {admin_user.id})")
        
        # Verificar resultado
        remaining_sales = db.query(Sale).filter(Sale.user_id == None).count()
        print(f"Vendas restantes sem usuário: {remaining_sales}")
        
    except Exception as e:
        db.rollback()
        print(f"Erro durante a migração: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=== MIGRAÇÃO DE VENDAS - ASSOCIANDO USUÁRIOS ===")
    migrate_sales_users()
    print("=== MIGRAÇÃO CONCLUÍDA ===")