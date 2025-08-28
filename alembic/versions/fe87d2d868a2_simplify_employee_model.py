"""simplify_employee_model

Revision ID: fe87d2d868a2
Revises: fix_old_payment_methods
Create Date: 2025-08-28 14:43:29.452117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fe87d2d868a2'
down_revision: Union[str, None] = 'fix_old_payment_methods'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adicionar colunas como nullable primeiro
    op.add_column('employees', sa.Column('full_name', sa.String(length=200), nullable=True))
    op.add_column('employees', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('employees', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('employees', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('employees', sa.Column('can_manage_inventory', sa.Boolean(), nullable=True))
    op.add_column('employees', sa.Column('can_manage_expenses', sa.Boolean(), nullable=True))
    op.add_column('employees', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Preencher os dados existentes
    op.execute("""
        UPDATE employees 
        SET 
            full_name = name,
            username = LOWER(REPLACE(name, ' ', '_') || id),
            password_hash = 'temporary_password_needs_reset',
            is_admin = CASE WHEN position ILIKE '%admin%' THEN TRUE ELSE FALSE END,
            can_manage_inventory = FALSE,
            can_manage_expenses = FALSE
    """)
    
    # Agora alterar as colunas para NOT NULL
    op.alter_column('employees', 'full_name', nullable=False)
    op.alter_column('employees', 'username', nullable=False)
    op.alter_column('employees', 'password_hash', nullable=False)
    op.alter_column('employees', 'is_admin', nullable=False)
    op.alter_column('employees', 'can_manage_inventory', nullable=False)
    op.alter_column('employees', 'can_manage_expenses', nullable=False)
    
    # Criar índices e constraints
    op.create_index(op.f('ix_employees_full_name'), 'employees', ['full_name'], unique=False)
    op.create_index(op.f('ix_employees_username'), 'employees', ['username'], unique=True)
    op.create_foreign_key(None, 'employees', 'users', ['user_id'], ['id'])
    
    # Remover colunas antigas
    op.drop_index(op.f('ix_employees_cpf'), table_name='employees')
    op.drop_index(op.f('ix_employees_email'), table_name='employees')
    op.drop_index(op.f('ix_employees_name'), table_name='employees')
    op.drop_column('employees', 'position')
    op.drop_column('employees', 'department')
    op.drop_column('employees', 'address')
    op.drop_column('employees', 'state')
    op.drop_column('employees', 'name')
    op.drop_column('employees', 'hire_date')
    op.drop_column('employees', 'email')
    op.drop_column('employees', 'cpf')
    op.drop_column('employees', 'city')
    op.drop_column('employees', 'phone')
    op.drop_column('employees', 'zip_code')


def downgrade() -> None:
    # Adicionar colunas antigas
    op.add_column('employees', sa.Column('zip_code', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('cpf', sa.VARCHAR(length=14), autoincrement=False, nullable=True))  # Alterado para nullable
    op.add_column('employees', sa.Column('email', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('hire_date', sa.DATE(), autoincrement=False, nullable=True))  # Alterado para nullable
    op.add_column('employees', sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=True))  # Alterado para nullable
    op.add_column('employees', sa.Column('state', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('address', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('department', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('employees', sa.Column('position', sa.VARCHAR(length=100), autoincrement=False, nullable=True))  # Alterado para nullable
    
    # Preencher dados antigos (não podemos recuperar todos os dados originais, então definimos valores padrão)
    op.execute("""
        UPDATE employees 
        SET 
            name = full_name,
            email = username || '@example.com',
            cpf = '000.000.000-00',
            position = CASE WHEN is_admin THEN 'Administrador' ELSE 'Funcionário' END,
            department = 'Geral',
            hire_date = CURRENT_DATE
    """)
    
    # Remover colunas novas
    op.drop_constraint(None, 'employees', type_='foreignkey')
    op.drop_index(op.f('ix_employees_username'), table_name='employees')
    op.drop_index(op.f('ix_employees_full_name'), table_name='employees')
    op.create_index(op.f('ix_employees_name'), 'employees', ['name'], unique=False)
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=True)
    op.create_index(op.f('ix_employees_cpf'), 'employees', ['cpf'], unique=True)
    
    # Alterar colunas não nulas
    op.alter_column('employees', 'name', nullable=False)
    op.alter_column('employees', 'hire_date', nullable=False)
    op.alter_column('employees', 'position', nullable=False)
    
    # Remover colunas novas
    op.drop_column('employees', 'user_id')
    op.drop_column('employees', 'can_manage_expenses')
    op.drop_column('employees', 'can_manage_inventory')
    op.drop_column('employees', 'is_admin')
    op.drop_column('employees', 'password_hash')
    op.drop_column('employees', 'username')
    op.drop_column('employees', 'full_name')
