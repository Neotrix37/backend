"""Add sync columns to all tables

Revision ID: add_sync_columns
Revises: fe87d2d868a2
Create Date: 2025-08-31 17:11:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# Identificadores de revisão usados pelo Alembic
revision = 'add_sync_columns'
down_revision = 'fe87d2d868a2'
branch_labels = None
depends_on = None

def get_tables(connection):
    inspector = inspect(connection)
    return inspector.get_table_names()

def upgrade():
    connection = op.get_bind()
    tables = get_tables(connection)
    
    # Lista de tabelas que precisam das colunas de sincronização
    target_tables = [
        'users',
        'products',
        'categories',
        'customers',
        'employees',
        'sales',
        'sale_items'
    ]
    
    # Filtra apenas as tabelas que existem no banco de dados
    existing_tables = [t for t in target_tables if t in tables]
    
    # Adiciona as colunas a cada tabela existente
    for table in existing_tables:
        # Adiciona a coluna last_updated se não existir
        op.add_column(
            table,
            sa.Column('last_updated', 
                     sa.DateTime(timezone=True), 
                     server_default=sa.func.now(),
                     nullable=False)
        )
        
        # Adiciona a coluna synced se não existir
        op.add_column(
            table,
            sa.Column('synced', 
                     sa.Boolean(), 
                     server_default='false',
                     nullable=False)
        )
        
        # Cria um índice na coluna last_updated para melhorar consultas de sincronização
        op.create_index(f'idx_{table}_last_updated', table, ['last_updated'])


def downgrade():
    connection = op.get_bind()
    tables = get_tables(connection)
    
    # Lista de tabelas que podem ter as colunas de sincronização
    target_tables = [
        'users',
        'products',
        'categories',
        'customers',
        'employees',
        'sales',
        'sale_items'
    ]
    
    # Filtra apenas as tabelas que existem no banco de dados
    existing_tables = [t for t in target_tables if t in tables]
    
    # Remove as colunas de cada tabela existente
    for table in existing_tables:
        # Remove o índice
        op.drop_index(f'idx_{table}_last_updated', table_name=table)
        
        # Remove as colunas se existirem
        op.drop_column(table, 'synced')
        op.drop_column(table, 'last_updated')
