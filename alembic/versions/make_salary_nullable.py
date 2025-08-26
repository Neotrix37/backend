"""make_salary_nullable

Revision ID: make_salary_nullable
Revises: add_salary_to_users
Create Date: 2025-08-26 08:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Identificação da revisão
revision = 'make_salary_nullable'
down_revision = 'add_salary_to_users'
branch_labels = None
depends_on = None

def upgrade():
    # Tornar a coluna nullable e definir valor padrão
    op.alter_column('users', 'salary',
                   existing_type=sa.Numeric(10, 2),
                   nullable=True,
                   server_default='1500.00')
    print("✅ Coluna 'salary' atualizada para aceitar valores nulos com valor padrão 1500.00")

def downgrade():
    # Reverter para NOT NULL com valor padrão 0.00
    op.execute("UPDATE users SET salary = 0.00 WHERE salary IS NULL")
    op.alter_column('users', 'salary',
                   existing_type=sa.Numeric(10, 2),
                   nullable=False,
                   server_default='0.00')
    print("✅ Coluna 'salary' revertida para NOT NULL com valor padrão 0.00")
