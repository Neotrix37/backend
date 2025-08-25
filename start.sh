#!/bin/bash
set -e

echo " Iniciando configuração da aplicação..."

# Carregar variáveis de ambiente do arquivo .env.production se existir
if [ -f ".env.production" ]; then
    echo " Carregando variáveis de ambiente de .env.production..."
    export $(grep -v '^#' .env.production | xargs)
fi

# Configurações padrão
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}
: ${DEBUG:="False"}

echo " Ambiente: $ENVIRONMENT"
echo " Modo Debug: $DEBUG"

# Verificar se a porta está disponível
if ! command -v lsof &> /dev/null || ! lsof -i :"$PORT" > /dev/null; then
    echo " Porta $PORT está disponível"
else
    echo "  Aviso: A porta $PORT já está em uso"
    echo "Tentando encontrar uma porta disponível..."
    PORT=$(($PORT + 1))
    echo "Usando a porta alternativa: $PORT"
fi

echo "\n Verificando dependências..."

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo " Python 3 não encontrado. Por favor, instale o Python 3.8 ou superior."
    exit 1
fi

echo " Python $(python3 --version | cut -d ' ' -f2) detectado"

echo "\n Verificando conexão com o PostgreSQL..."

# Verificar se a variável DATABASE_URL está definida
if [ -z "$DATABASE_URL" ]; then
    echo " 🔍 Verificando configuração do banco de dados..."
    echo " ⚠️  ATENÇÃO: DATABASE_URL não está definida"
    
    # Tentar usar a variável interna do Railway
    if [ -n "$RAILWAY_POSTGRESQL_URL" ]; then
        echo " ℹ️  Usando RAILWAY_POSTGRESQL_URL para conexão com o banco de dados"
        export DATABASE_URL="$RAILWAY_POSTGRESQL_URL"
    elif [ -n "$DATABASE_URL_INTERNAL" ]; then
        echo " ℹ️  Usando DATABASE_URL_INTERNAL para conexão com o banco de dados"
        export DATABASE_URL="$DATABASE_URL_INTERNAL"
    else
        echo " ❌ ERRO: Nenhuma configuração de banco de dados encontrada"
        echo " ℹ️  Certifique-se de que o plugin PostgreSQL está adicionado ao seu projeto no Railway"
        echo " ℹ️  Variáveis de ambiente disponíveis:"
        env | sort
        exit 1
    fi
fi

echo " 🔧 Configurações carregadas:"
echo "- ENVIRONMENT: ${ENVIRONMENT}"
echo "- HOST: ${HOST}"
echo "- PORT: ${PORT}"
echo "- DEBUG: ${DEBUG}"
echo "- DATABASE_URL: ${DATABASE_URL:0:30}..."

# Extrair informações de conexão da variável DATABASE_URL
if [[ $DATABASE_URL =~ postgres(ql)?://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[2]}"
    DB_PASS="${BASH_REMATCH[3]}"
    DB_HOST="${BASH_REMATCH[4]}"
    DB_PORT="${BASH_REMATCH[5]}"
    DB_NAME="${BASH_REMATCH[6]}"
    
    echo " Conectando ao PostgreSQL em $DB_HOST:$DB_PORT como $DB_USER (banco: $DB_NAME)"
    
    # Exportar variáveis para o PGPASSWORD
    export PGHOST=$DB_HOST
    export PGPORT=$DB_PORT
    export PGDATABASE=$DB_NAME
    export PGUSER=$DB_USER
    export PGPASSWORD=$DB_PASS
else
    echo "  Não foi possível analisar a DATABASE_URL, usando como está"
    export PGDATABASE=$(echo $DATABASE_URL | grep -oP '\/[^/]+$' | cut -d'/' -f2)
fi

# Instalar dependências se não estiverem instaladas
echo "\n Verificando dependências Python..."
pip install -q -r requirements.txt

# Executar migrações do Alembic
echo "\n Executando migrações do banco de dados..."
alembic upgrade head || echo " ⚠️  Aviso: Falha ao executar migrações. Continuando..."

echo " Iniciando aplicação..."
echo "   Host: $HOST"
echo "   Porta: $PORT"
echo "   Ambiente: $ENVIRONMENT"
echo "   Debug: $DEBUG"

# Iniciar o Gunicorn com as configurações
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    main:app