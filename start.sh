#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
sleep 5

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting application..."
exec gunicorn main:app -c gunicorn_config.py