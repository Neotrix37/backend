"""merge heads

Revision ID: 3901e0af53cd
Revises: 7d4708e70d76, 1234567890ab
Create Date: 2025-08-28 09:42:12.700567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3901e0af53cd'
down_revision: Union[str, None] = ('7d4708e70d76', '1234567890ab')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
