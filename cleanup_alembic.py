from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def main():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Obtém a URL do banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não encontrada nas variáveis de ambiente.")
        print("Certifique-se de ter um arquivo .env com DATABASE_URL configurada.")
        return
    
    try:
        # Cria a conexão com o banco de dados
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Remove a tabela alembic_version se existir
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            
            # Cria uma nova tabela alembic_version vazia
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL
                )
            """))
            
            conn.commit()
            print("✅ Tabela alembic_version resetada com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao limpar a tabela alembic_version: {e}")

if __name__ == "__main__":
    print("Iniciando limpeza da tabela alembic_version...")
    main()
    print("Processo finalizado.")
    print("\nPróximos passos:")
    print("1. Execute: alembic revision -m \"initial\" --head=base")
    print("2. Execute: alembic upgrade head")
