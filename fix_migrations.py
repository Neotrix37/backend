#!/usr/bin/env python3
"""
Script para corrigir o problema de múltiplas heads no Alembic.
"""
import os
import sys
from alembic.config import Config
from alembic import command

def fix_migrations():
    # Configuração do Alembic
    alembic_cfg = Config("alembic.ini")
    
    print("🔍 Verificando migrações...")
    
    # Listar todas as revisões
    print("\n📋 Revisões disponíveis:")
    command.heads(alembic_cfg)
    
    # Obter todas as heads
    script = command.revision(alembic_cfg, rev_id="fix_heads", head="heads", splice=True)
    
    print("\n🔄 Criando migração de correção...")
    command.revision(alembic_cfg, autogenerate=True, message="Fix multiple heads")
    
    # Aplicar as migrações
    print("\n🔄 Aplicando migrações...")
    command.upgrade(alembic_cfg, "head")
    
    print("\n✅ Migrações corrigidas com sucesso!")

if __name__ == "__main__":
    try:
        fix_migrations()
    except Exception as e:
        print(f"❌ Erro ao corrigir migrações: {e}", file=sys.stderr)
        sys.exit(1)
