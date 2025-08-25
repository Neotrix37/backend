#!/bin/bash
set -e

echo "Verificando conexão com o banco de dados..."
if ! python -c "import os; from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); print('Conexão com o banco de dados bem-sucedida!'); conn.close()"; then
    echo "Erro: Falha ao conectar ao banco de dados"
    exit 1
fi

echo "Aplicando migrações do banco de dados..."
alembic upgrade head

echo "Iniciando aplicação na porta ${PORT}..."
exec gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    main:app

# Se o gunicorn falhar, mostre a mensagem de erro
echo "Falha ao iniciar o servidor Gunicorn"
exit 1
