"""add_can_sell_to_employees

Revision ID: add_can_sell
Revises: add_is_admin
Create Date: 2023-11-15 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_can_sell'
down_revision: Union[str, None] = 'add_is_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add can_sell column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='employees' AND column_name='can_sell') THEN
            ALTER TABLE employees ADD COLUMN can_sell BOOLEAN DEFAULT TRUE NOT NULL;
        END IF;
    END
    $$;
    """)


def downgrade() -> None:
    # Remove can_sell column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='employees' AND column_name='can_sell') THEN
            ALTER TABLE employees DROP COLUMN can_sell;
        END IF;
    END
    $$;
    """)