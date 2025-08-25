import os

# Configuração do Gunicorn para produção no Railway

# Número de workers (processos) - reduzido para evitar consumo excessivo de memória
workers = 2

# Tipo de worker - usando Uvicorn para FastAPI
worker_class = 'uvicorn.workers.UvicornWorker'

# Bind - endereço e porta para o servidor
bind = '0.0.0.0:' + str(int(os.environ.get('PORT', 8000)))

# Timeout em segundos
timeout = 120

# Configurações de log - redirecionando para stdout/stderr para o Railway
autoreload = True
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Configurações de segurança
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Configurações de processo
daemon = False
pidfile = 'gunicorn.pid'