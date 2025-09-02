# Configuração otimizada do Gunicorn para o Railway
import os
import multiprocessing

# Configurações básicas
bind = "0.0.0.0:8000"
workers = 2  # Reduzido para 2 workers para economizar recursos
worker_class = 'uvicorn.workers.UvicornWorker'

# Timeout e keepalive
timeout = 30  # Reduzido para 30 segundos
keepalive = 2

# Configurações de log
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True

# Formato do log de acesso
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%(M)s ms"'

# Configurações de desempenho
max_requests = 1000
max_requests_jitter = 50
worker_connections = 1000

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações adicionais para o Railway
preload_app = True  # Carrega a aplicação antes de forkar os workers
reload = os.getenv('DEBUG', 'False').lower() == 'true'

# Configuração de workers
if os.getenv('ENVIRONMENT') == 'development':
    reload = True
    workers = 1
    loglevel = 'debug'

# Configuração de diretório temporário
worker_tmp_dir = '/dev/shm' if os.path.exists('/dev/shm') else None