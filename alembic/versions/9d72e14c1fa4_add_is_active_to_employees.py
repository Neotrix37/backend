"""add_is_active_to_employees

Revision ID: 9d72e14c1fa4
Revises: f8eefa29ef34
Create Date: 2025-09-02 20:37:39.519027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d72e14c1fa4'
down_revision: Union[str, None] = 'f8eefa29ef34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='employees' AND column_name='is_active') THEN
            ALTER TABLE employees ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
        END IF;
    END
    $$;
    """)


def downgrade() -> None:
    # Remove is_active column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='employees' AND column_name='is_active') THEN
            ALTER TABLE employees DROP COLUMN is_active;
        END IF;
    END
    $$;
    """)
