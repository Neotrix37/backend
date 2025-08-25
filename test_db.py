from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv()

# Obtém a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Erro: DATABASE_URL não está definida no arquivo .env")
    exit(1)

try:
    # Tenta se conectar ao banco de dados
    print(f"Tentando conectar ao banco de dados em: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Conexão bem-sucedida!")
        
        # Testa uma consulta simples
        result = connection.execute(text("SELECT version();"))
        print(f"Versão do PostgreSQL: {result.scalar()}")
    
except SQLAlchemyError as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    
    # Verifica se o banco de dados está acessível
    if "Connection refused" in str(e):
        print("\nDica: O banco de dados pode não estar acessível. Verifique se:")
        print("1. O servidor PostgreSQL está rodando")
        print("2. O firewall permite conexões na porta 5432")
        print("3. As credenciais de acesso estão corretas")
        print("4. O banco de dados existe e está acessível")
    
    exit(1)
