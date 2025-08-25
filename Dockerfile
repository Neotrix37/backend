FROM python:3.11-slim

WORKDIR /app

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar o pip mais recente
RUN pip install --upgrade pip

# Copiar arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p logs

# Expor a porta que a aplicação usa
EXPOSE $PORT

# Comando para iniciar a aplicação em produção usando Gunicorn
CMD ["sh", "-c", "\
    echo 'Aplicando migrações do banco de dados...' && \
    alembic upgrade head && \
    echo 'Iniciando aplicação...' && \
    gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker main:app"]