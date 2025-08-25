"""merge_heads

Revision ID: merge_heads
Revises: f3bdf51afafe, fix_duplicate_venda_por_peso
Create Date: 2025-08-26 01:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_heads'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Esta é uma migração de mesclagem, não faz alterações no banco de dados
    pass

def downgrade() -> None:
    # Não faz nada no downgrade para uma migração de mesclagem
    pass
