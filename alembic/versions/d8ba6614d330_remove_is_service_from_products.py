"""remove_is_service_from_products

Revision ID: d8ba6614d330
Revises: 3901e0af53cd
Create Date: 2025-08-28 09:42:21.892393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8ba6614d330'
down_revision: Union[str, None] = '3901e0af53cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
