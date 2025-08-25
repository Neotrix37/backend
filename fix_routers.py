#!/usr/bin/env python3
"""
Script para verificar e corrigir a exportação dos roteadores nos arquivos de endpoint.
"""
import os
from pathlib import Path

# Diretório base dos endpoints
BASE_DIR = Path(__file__).parent / "app" / "api" / "api_v1" / "endpoints"

# Lista de arquivos de endpoint
ENDPOINT_FILES = [
    "auth.py",
    "products.py",
    "categories.py",
    "sales.py",
    "customers.py",
    "employees.py",
    "inventory.py",
    "users.py"
]

def check_and_fix_router_export(file_path):
    """Verifica e corrige a exportação do router em um arquivo de endpoint."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verifica se já tem a exportação do router
    if "__all__ = [\"router\"]" in content:
        print(f"✅ {file_path.name} já está configurado corretamente.")
        return False
    
    # Adiciona a exportação do router no final do arquivo
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n\n# Exportar o router\n__all__ = [\"router\"]\n")
    
    print(f"✅ Corrigido: {file_path.name}")
    return True

def main():
    print("🔍 Verificando arquivos de endpoint...\n")
    
    fixed_count = 0
    for filename in ENDPOINT_FILES:
        file_path = BASE_DIR / filename
        if file_path.exists():
            if check_and_fix_router_export(file_path):
                fixed_count += 1
    
    print(f"\n✅ Verificação concluída. {fixed_count} arquivos foram corrigidos.")

if __name__ == "__main__":
    main()
