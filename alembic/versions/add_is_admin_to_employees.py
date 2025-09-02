"""add_is_admin_to_employees

Revision ID: add_is_admin
Revises: fe87d2d868a2
Create Date: 2023-11-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_is_admin'
down_revision: Union[str, None] = 'fe87d2d868a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_admin column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='employees' AND column_name='is_admin') THEN
            ALTER TABLE employees ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
        END IF;
    END
    $$;
    """)


def downgrade() -> None:
    # Remove is_admin column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='employees' AND column_name='is_admin') THEN
            ALTER TABLE employees DROP COLUMN is_admin;
        END IF;
    END
    $$;
    """)