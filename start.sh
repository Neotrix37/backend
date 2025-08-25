#!/bin/bash
set -e

echo "Starting application setup..."

# Carregar variáveis de ambiente do arquivo .env.production se existir
if [ -f ".env.production" ]; then
    echo "Loading .env.production file..."
    export $(grep -v '^#' .env.production | xargs)
fi

echo "Waiting for PostgreSQL to start..."

# Verificar se a variável DATABASE_URL está definida
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not defined"
    echo "Available environment variables:"
    env | sort
    exit 1
fi

echo "Using DATABASE_URL: ${DATABASE_URL}"

# Extrair informações de conexão da variável DATABASE_URL
if [[ $DATABASE_URL =~ postgres(ql)?://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[2]}"
    DB_PASS="${BASH_REMATCH[3]}"
    DB_HOST="${BASH_REMATCH[4]}"
    DB_PORT="${BASH_REMATCH[5]}"
    DB_NAME="${BASH_REMATCH[6]}"
    echo "Connecting to PostgreSQL at $DB_HOST:$DB_PORT as $DB_USER (database: $DB_NAME)"
    
    # Exportar variáveis para o PGPASSWORD
    export PGHOST=$DB_HOST
    export PGPORT=$DB_PORT
    export PGDATABASE=$DB_NAME
    export PGUSER=$DB_USER
    export PGPASSWORD=$DB_PASS
else
    echo "WARNING: Could not parse DATABASE_URL, using it as is"
    # Tentar extrair informações de forma mais simples
    export PGDATABASE=$(echo $DATABASE_URL | grep -oP '\/[^/]+$' | cut -d'/' -f2)
fi

# Aguardar até que o PostgreSQL esteja disponível
echo "Checking PostgreSQL connection..."
MAX_RETRIES=30
RETRIES=0

until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" || [ $RETRIES -eq $MAX_RETRIES ]; do
    echo "Waiting for PostgreSQL to be available... ${RETRIES}/${MAX_RETRIES}"
    RETRIES=$((RETRIES+1))
    sleep 2
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo "ERROR: Failed to connect to PostgreSQL after $MAX_RETRIES attempts"
    echo "PGHOST: $PGHOST"
    echo "PGPORT: $PGPORT"
    echo "PGDATABASE: $PGDATABASE"
    echo "PGUSER: $PGUSER"
    exit 1
fi

echo "PostgreSQL is available!"

# Executar migrações do banco de dados
echo "Running database migrations..."
python -m alembic upgrade head

# Iniciar a aplicação
echo "Starting application..."
exec gunicorn main:app -c gunicorn_config.py