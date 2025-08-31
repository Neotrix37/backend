"""merge heads

Revision ID: 27e6810cfc59
Revises: 20250831180200, add_sync_columns
Create Date: 2025-08-31 20:10:06.971675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27e6810cfc59'
down_revision: Union[str, None] = ('20250831180200', 'add_sync_columns')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
