import os
import multiprocessing

# Configurações gerais do Gunicorn
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Máximo de 4 workers
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Configurações de logging
loglevel = 'info'
accesslog = '-'  # Log para stdout
errorlog = '-'   # Log de erros para stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s %(D)s %({X-Request-Id}i)s %({X-Forwarded-For}i)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de desempenho
preload_app = True  # Carrega a aplicação antes de forking workers

# Configurações específicas para Uvicorn
worker_tmp_dir = '/dev/shm'  # Usa memória compartilhada para arquivos temporários

# Configurações de timeout
graceful_timeout = 30  # Tempo para workers finalizarem requisições antes de serem encerrados