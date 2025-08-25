"""add refresh_token to users

Revision ID: 4a5b6c7d8e9f0
Revises: f3bdf51afafe
Create Date: 2025-08-25 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a5b6c7d8e9f0'
down_revision: str = 'f3bdf51afafe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adicionar a coluna refresh_token à tabela users
    op.add_column(
        'users',
        sa.Column('refresh_token', sa.String(length=512), nullable=True, comment='Token de atualização JWT')
    )
    
    # Criar índice para melhorar a busca por refresh_token
    op.create_index(
        'ix_users_refresh_token', 
        'users', 
        ['refresh_token'], 
        unique=False
    )


def downgrade() -> None:
    # Remover o índice
    op.drop_index('ix_users_refresh_token', table_name='users')
    
    # Remover a coluna refresh_token
    op.drop_column('users', 'refresh_token')
