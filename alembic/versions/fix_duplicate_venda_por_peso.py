"""fix_duplicate_venda_por_peso

Revision ID: fix_duplicate_venda_por_peso
Revises: f3bdf51afafe
Create Date: 2025-08-26 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_duplicate_venda_por_peso'
down_revision: Union[str, None] = 'f3bdf51afafe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Verifica se a coluna já existe antes de tentar adicioná-la
    conn = op.get_bind()
    inspector = sa.inspect(conn.engine)
    columns = [col['name'] for col in inspector.get_columns('products')]
    
    if 'venda_por_peso' not in columns:
        op.add_column('products', sa.Column('venda_por_peso', sa.Boolean(), 
                     server_default=sa.false(), nullable=False))
    
    # Se a coluna existir, garante que tem o valor padrão correto
    op.alter_column('products', 'venda_por_peso', 
                   existing_type=sa.BOOLEAN(),
                   server_default=sa.false(),
                   nullable=False)

def downgrade() -> None:
    # Não faz nada no downgrade para evitar problemas
    pass
