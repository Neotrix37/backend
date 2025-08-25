# Configuração do Gunicorn para produção

# Número de workers (processos) - recomendado: (2 x núcleos) + 1
workers = 4

# Tipo de worker - usando Uvicorn para FastAPI
worker_class = 'uvicorn.workers.UvicornWorker'

# Bind - endereço e porta para o servidor
bind = '0.0.0.0:8000'

# Timeout em segundos
timeout = 120

# Configurações de log
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Configurações de segurança
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Configurações de processo
daemon = False
pidfile = 'gunicorn.pid'