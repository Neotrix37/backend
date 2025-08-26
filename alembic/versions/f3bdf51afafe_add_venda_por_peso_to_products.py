"""add_venda_por_peso_to_products

Revision ID: f3bdf51afafe
Revises: c162b555c015
Create Date: 2025-08-18 07:05:11.744830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'f3bdf51afafe'
down_revision: Union[str, None] = 'c162b555c015'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(column['name'] == column_name for column in columns)

def upgrade() -> None:
    # Verifica se a coluna já existe antes de adicionar
    if not column_exists('products', 'venda_por_peso'):
        op.add_column('products', sa.Column('venda_por_peso', sa.Boolean(), nullable=True, server_default='false'))
        # Atualiza os registros existentes para evitar problemas com NOT NULL
        op.execute("UPDATE products SET venda_por_peso = false WHERE venda_por_peso IS NULL")
        # Altera a coluna para NOT NULL
        op.alter_column('products', 'venda_por_peso', nullable=False)


def downgrade() -> None:
    if column_exists('products', 'venda_por_peso'):
        op.drop_column('products', 'venda_por_peso')
