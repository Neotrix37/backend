# Configuração do Gunicorn para produção no Railway
import os
import multiprocessing

# Número de workers (processos)
workers = multiprocessing.cpu_count() * 2 + 1  # Ajuste conforme necessário para o ambiente do Railway

# Tipo de worker - usando Uvicorn para FastAPI
worker_class = 'uvicorn.workers.UvicornWorker'

# Bind - endereço e porta para o servidor
bind = '0.0.0.0:' + os.getenv('PORT', '8000')

# Timeout em segundos
timeout = 120

# Configurações de log
accesslog = '-'  # Log para stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
errorlog = '-'    # Log de erros para stderr
loglevel = 'info'

# Configurações de segurança
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Configurações de processo
daemon = False
preload_app = True  # Carrega a aplicação antes de forking

# Configurações adicionais para o Railway
worker_tmp_dir = '/dev/shm' if os.path.exists('/dev/shm') else None

# Configuração de workers baseada em CPU
worker_connections = 1000

# Configuração de logs
capture_output = True
enable_stdio_inheritance = True