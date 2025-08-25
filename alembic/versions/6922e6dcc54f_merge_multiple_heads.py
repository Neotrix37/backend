"""merge multiple heads

Revision ID: 6922e6dcc54f
Revises: 6d2556dab0aa, 4a5b6c7d8e9f0
Create Date: 2025-08-26 00:39:22.465054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6922e6dcc54f'
down_revision: Union[str, None] = ('6d2556dab0aa', '4a5b6c7d8e9f0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
