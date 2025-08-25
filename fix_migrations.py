import os
import sys
from alembic.config import Config
from alembic import command

def fix_migrations():
    # Configuração do Alembic
    alembic_cfg = Config("alembic.ini")
    
    # 1. Marcar todas as migrações como head
    command.heads(alembic_cfg, "heads", verbose=True)
    
    # 2. Forçar o upgrade para a última migração
    command.upgrade(alembic_cfg, "heads")
    
    print("\n✅ Migrações corrigidas com sucesso!")

if __name__ == "__main__":
    fix_migrations()
