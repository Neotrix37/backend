FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os arquivos necessários primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto da aplicação
COPY . .

# Tornar o script de inicialização executável
RUN chmod +x /app/start.sh

# Porta que a aplicação vai usar
EXPOSE 8000

# Comando de inicialização
CMD ["./start.sh"]