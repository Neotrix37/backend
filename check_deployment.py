import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica a versão do Python."""
    print("🔍 Verificando versão do Python...")
    python_version = sys.version.split()[0]
    print(f"✅ Python {python_version} detectado")
    return python_version

def check_environment_variables():
    """Verifica as variáveis de ambiente necessárias."""
    print("\n🔍 Verificando variáveis de ambiente...")
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        print("Por favor, defina essas variáveis no arquivo .env ou no painel do Railway")
        return False
    
    print("✅ Todas as variáveis de ambiente necessárias estão definidas")
    return True

def check_database_connection():
    """Tenta conectar ao banco de dados."""
    print("\n🔍 Testando conexão com o banco de dados...")
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL não definida")
            return False
            
        # Extrai as credenciais da URL
        parsed = urlparse(db_url)
        dbname = parsed.path[1:]
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        print("✅ Conexão com o banco de dados bem-sucedida!")
        return True
        
    except Exception as e:
        print(f"❌ Falha ao conectar ao banco de dados: {str(e)}")
        return False

def run_migrations():
    """Executa as migrações do banco de dados."""
    print("\n🔄 Executando migrações do banco de dados...")
    try:
        # Tenta executar as migrações
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migrações aplicadas com sucesso!")
            return True
        else:
            print("❌ Erro ao executar migrações:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {str(e)}")
        return False

def main():
    print("\n🔧 Verificação de Configuração do Projeto 🔧")
    print("=" * 50)
    
    # Verifica a versão do Python
    check_python_version()
    
    # Verifica as variáveis de ambiente
    if not check_environment_variables():
        return 1
    
    # Verifica a conexão com o banco de dados
    if not check_database_connection():
        return 1
    
    # Executa as migrações
    if not run_migrations():
        return 1
    
    print("\n✨ Todas as verificações foram concluídas com sucesso!")
    print("O aplicativo está pronto para ser iniciado.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
