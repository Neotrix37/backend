#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."

# Extrair informações de conexão da variável DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL não está definida"
    exit 1
fi

# Extrair host e usuário da DATABASE_URL
# Formato esperado: postgresql://username:password@hostname:port/database
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
    echo "Conectando ao PostgreSQL em $DB_HOST:$DB_PORT como $DB_USER (database: $DB_NAME)"
else
    echo "AVISO: Não foi possível extrair informações da DATABASE_URL usando regex"
    echo "Tentando conexão direta usando a DATABASE_URL completa"
fi

# Aguardar até que o PostgreSQL esteja disponível
echo "Verificando conexão com o PostgreSQL..."
MAX_RETRIES=30
RETRIES=0

until { [[ -n "$DB_HOST" ]] && pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT"; } || \
      { [[ -z "$DB_HOST" ]] && pg_isready -d "$DATABASE_URL"; } || \
      [ $RETRIES -eq $MAX_RETRIES ]; do
    echo "Aguardando PostgreSQL ficar disponível... ${RETRIES}/${MAX_RETRIES}"
    RETRIES=$((RETRIES+1))
    sleep 2
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo "ERROR: Falha ao conectar ao PostgreSQL após $MAX_RETRIES tentativas"
    exit 1
fi

echo "PostgreSQL está disponível!"

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting application..."
exec gunicorn main:app -c gunicorn_config.py