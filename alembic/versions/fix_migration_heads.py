"""fix_migration_heads

Revision ID: fix_migration_heads
Revises: 6d2556dab0aa, add_salary_default
Create Date: 2025-08-26 09:21:00.000000

"""
from alembic import op

# Identificação da revisão
revision = 'fix_migration_heads'
down_revision = ('6d2556dab0aa', 'add_salary_default')
branch_labels = None
depends_on = None

def upgrade():
    # Esta migração não faz alterações no banco de dados
    # Apenas serve para consolidar as migrações
    pass

def downgrade():
    # Não há downgrade para esta migração
    pass
