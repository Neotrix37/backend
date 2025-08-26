"""add_salary_to_users

Revision ID: add_salary_to_users
Revises: 6d2556dab0aa
Create Date: 2025-08-26 06:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_salary_to_users'
down_revision = '6d2556dab0aa'
branch_labels = None
depends_on = None

def upgrade():
    # Verifica se a coluna já existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('users')]
    
    if 'salary' not in columns:
        # Adiciona a coluna como nullable primeiro
        op.add_column('users', sa.Column('salary', sa.Numeric(10, 2), nullable=True))
        
        # Atualiza os registros existentes para evitar problemas com NOT NULL
        op.execute("UPDATE users SET salary = 0.00")
        
        # Altera para NOT NULL
        op.alter_column('users', 'salary', nullable=False, server_default='0.00')
        
        print("✅ Coluna 'salary' adicionada com sucesso à tabela 'users'")
    else:
        print("ℹ️  A coluna 'salary' já existe na tabela 'users'")

def downgrade():
    # Remove a coluna
    op.drop_column('users', 'salary')
    print("✅ Coluna 'salary' removida da tabela 'users'")
