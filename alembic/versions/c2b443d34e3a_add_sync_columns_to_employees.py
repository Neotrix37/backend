"""add_sync_columns_to_employees

Revision ID: c2b443d34e3a
Revises: add_sync_columns
Create Date: 2025-09-02 22:42:50.618614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2b443d34e3a'
down_revision: Union[str, None] = 'add_sync_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add last_updated and synced columns to employees table
    op.add_column('employees', sa.Column('last_updated', sa.DateTime(timezone=True),
                                      server_default=sa.text('now()'),
                                      nullable=False))
    op.add_column('employees', sa.Column('synced', sa.Boolean(),
                                      server_default=sa.text('false'),
                                      nullable=False))
    op.create_index('idx_employees_last_updated', 'employees', ['last_updated'])


def downgrade() -> None:
    # Remove last_updated and synced columns from employees table
    op.drop_index('idx_employees_last_updated', table_name='employees')
    op.drop_column('employees', 'synced')
    op.drop_column('employees', 'last_updated')
