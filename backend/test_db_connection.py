import psycopg2
import time
import sys

def test_connection():
    max_retries = 5
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1} de conexão com o banco de dados...")
            conn = psycopg2.connect(
                dbname="railway",
                user="postgres",
                password="PVVHzsCZDuQiwnuziBfcgukYLCuCxdau",
                host="interchange.proxy.rlwy.net",
                port="33939"
            )
            
            # Testar a conexão
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print("\n✅ Conexão bem-sucedida!")
                print(f"Versão do PostgreSQL: {version[0]}")
                
                # Verificar tabelas existentes
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                print("\n📋 Tabelas no banco de dados:")
                for table in tables:
                    print(f"- {table[0]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro na tentativa {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Aguardando {retry_delay} segundos antes de tentar novamente...\n")
                time.sleep(retry_delay)
    
    print("\n⚠️ Não foi possível conectar ao banco de dados após várias tentativas.")
    return False

if __name__ == "__main__":
    test_connection()
