FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p logs

# Expor a porta que a aplicação usa
EXPOSE 8000

# Adicionar script de inicialização
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Comando para iniciar a aplicação em produção
CMD ["/app/start.sh"]