"""add_sync_columns

Revision ID: add_sync_columns
Revises: 9d72e14c1fa4
Create Date: 2025-09-02 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_sync_columns'
down_revision: Union[str, None] = '9d72e14c1fa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add last_updated and synced columns to all tables
    tables = ['products', 'categories', 'customers', 'sales', 'sale_items', 'users']
    
    for table in tables:
        op.add_column(table, sa.Column('last_updated', postgresql.TIMESTAMP(timezone=True),
                                      server_default=sa.text('now()'),
                                      nullable=False))
        op.add_column(table, sa.Column('synced', sa.BOOLEAN(),
                                      server_default=sa.text('false'),
                                      nullable=False))
        op.create_index(f'idx_{table}_last_updated', table, ['last_updated'])

def downgrade() -> None:
    # Remove last_updated and synced columns from all tables
    tables = ['products', 'categories', 'customers', 'sales', 'sale_items', 'users']
    
    for table in tables:
        op.drop_index(f'idx_{table}_last_updated', table_name=table)
        op.drop_column(table, 'synced')
        op.drop_column(table, 'last_updated')