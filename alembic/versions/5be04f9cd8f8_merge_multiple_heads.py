"""merge multiple heads

Revision ID: 5be04f9cd8f8
Revises: 6d2556dab0aa, 4a5b6c7d8e9f0
Create Date: 2025-08-26 00:25:10.193499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5be04f9cd8f8'
down_revision: Union[str, None] = ('6d2556dab0aa', '4a5b6c7d8e9f0')
branch_labels: Union[str, Sequence[str], None] = ('merge_heads',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
