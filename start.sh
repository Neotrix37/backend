#!/bin/bash
set -e

echo " Iniciando configuração da aplicação..."

# Carregar variáveis de ambiente do arquivo .env.production se existir
if [ -f ".env.production" ]; then
    echo " Carregando variáveis de ambiente de .env.production..."
    # Remover linhas de comentário e exportar variáveis
    while IFS= read -r line || [ -n "$line" ]; do
        # Pular linhas vazias e comentários
        if [[ "$line" =~ ^[^#]*= && ! "$line" =~ ^[[:space:]]*# ]]; then
            # Remover espaços em branco extras e exportar
            export "$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        fi
    done < .env.production
fi

# Configurações padrão
: ${HOST:="0.0.0.0"}
: ${PORT:=8000}
: ${ENVIRONMENT:="production"}
: ${DEBUG:="False"}

echo " Ambiente: $ENVIRONMENT"
echo " Modo Debug: $DEBUG"

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
    echo " ERRO: DATABASE_URL não está definida"
    echo "Variáveis de ambiente disponíveis:"
    env | sort
    exit 1
fi

echo " Usando DATABASE_URL: ${DATABASE_URL//:*/:*****}"

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

# Aguardar até que o PostgreSQL esteja disponível
echo " Aguardando o PostgreSQL ficar disponível..."
MAX_RETRIES=30
RETRIES=0

until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" || [ $RETRIES -eq $MAX_RETRIES ]; do
    RETRIES=$((RETRIES+1))
    echo "   Tentativa $RETRIES de $MAX_RETRIES..."
    sleep 2
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
    echo " Não foi possível conectar ao PostgreSQL após $MAX_RETRIES tentativas"
    echo "   Verifique suas credenciais e se o servidor está acessível"
    exit 1
fi

echo " PostgreSQL está disponível!"

# Executar migrações do Alembic
echo "\n Executando migrações do banco de dados..."
alembic upgrade head

# Instalar dependências se não estiverem instaladas
echo "\n Verificando dependências Python..."
pip install -q -r requirements.txt

# Iniciar a aplicação
echo "\n Iniciando a aplicação..."
echo "   Host: $HOST"
echo "   Porta: $PORT"
echo "   Ambiente: $ENVIRONMENT"
echo "   Debug: $DEBUG"

exec gunicorn \
    --bind "$HOST:$PORT" \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    main:app