"""add_salary_default

Revision ID: 1234567890ab
Revises: 6d2556dab0aa
Create Date: 2025-08-26 07:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identificação da revisão
revision = '1234567890ab'
down_revision = '6d2556dab0aa'
branch_labels = None
depends_on = None

def upgrade():
    # Alterar a coluna salary para ter um valor padrão
    op.alter_column('users', 'salary',
                   existing_type=sa.NUMERIC(10, 2),
                   server_default='1500.00',
                   nullable=True)

def downgrade():
    # Reverter a alteração, removendo o valor padrão
    op.alter_column('users', 'salary',
                   existing_type=sa.NUMERIC(10, 2),
                   server_default=None,
                   nullable=True)
