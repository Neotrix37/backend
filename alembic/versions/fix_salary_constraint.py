"""fix_salary_constraint

Revision ID: fix_salary_constraint
Revises: add_salary_to_users
Create Date: 2025-08-26 09:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Identificação da revisão
revision = 'fix_salary_constraint'
down_revision = 'add_salary_to_users'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Primeiro, definir um valor padrão para registros existentes
    op.execute("UPDATE users SET salary = 0.00 WHERE salary IS NULL")
    
    # 2. Remover a restrição NOT NULL e adicionar valor padrão
    op.alter_column('users', 'salary',
                   existing_type=sa.Numeric(10, 2),
                   nullable=True,
                   server_default='1500.00')
    
    print("✅ Restrição NOT NULL removida e valor padrão definido para o campo 'salary'")

def downgrade():
    # 1. Atualizar registros nulos para o valor padrão
    op.execute("UPDATE users SET salary = 0.00 WHERE salary IS NULL")
    
    # 2. Restaurar a restrição NOT NULL
    op.alter_column('users', 'salary',
                   existing_type=sa.Numeric(10, 2),
                   nullable=False,
                   server_default='0.00')
    
    print("✅ Restrição NOT NULL restaurada para o campo 'salary'")
