import os
import sys
import urllib.parse
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, exc

def fix_migrations():
    # Dados de conexão atualizados para usar o endpoint público
    db_config = {
        'username': 'postgres',
        'password': 'PVVHzsCZDuQiwnuziBfcgukYLCuCxdau',
        'host': 'monorail.proxy.rlwy.net',  # Usando o endpoint público
        'port': '33939',  # Verifique se esta é a porta correta
        'database': 'railway'
    }
    
    # Cria a URL de conexão manualmente
    db_url = f"postgresql://{db_config['username']}:{urllib.parse.quote_plus(db_config['password'])}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    print("Conectando ao banco de dados...")
    print(f"URL: postgresql://{db_config['username']}:******@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    try:
        # Configuração mínima para conexão
        engine = create_engine(db_url)
        
        # Testa a conexão básica primeiro
        with engine.connect() as connection:
            print("✅ Conexão bem-sucedida!")
            
            # Verifica se a tabela alembic_version existe
            if not engine.dialect.has_table(connection, 'alembic_version'):
                print("ℹ️  Tabela alembic_version não encontrada. Criando...")
                config = Config("alembic.ini")
                command.stamp(config, "head")
                print("✅ Tabela alembic_version criada com sucesso!")
                return
            
            # Obtém a versão atual do banco de dados
            result = connection.execute("SELECT version_num FROM alembic_version").fetchone()
            if not result:
                print("ℹ️  Nenhuma versão encontrada. Marcando como head...")
                config = Config("alembic.ini")
                command.stamp(config, "head")
                return
                
            current_rev = result[0]
            print(f"ℹ️  Versão atual do banco: {current_rev}")
            
            # Força a marcação da versão mais recente como head
            print("🔄 Atualizando para a versão mais recente...")
            config = Config("alembic.ini")
            command.stamp(config, "head", purge=True)
            
            print("✅ Migrações corrigidas com sucesso!")
            
    except exc.SQLAlchemyError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        print("Verifique se as credenciais e o host estão corretos.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    fix_migrations()
