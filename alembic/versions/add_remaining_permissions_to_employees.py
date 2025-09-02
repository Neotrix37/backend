"""add_remaining_permissions_to_employees

Revision ID: add_permissions
Revises: add_can_sell
Create Date: 2023-11-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_permissions'
down_revision: Union[str, None] = 'add_can_sell'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add can_manage_inventory column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='employees' AND column_name='can_manage_inventory') THEN
            ALTER TABLE employees ADD COLUMN can_manage_inventory BOOLEAN DEFAULT FALSE NOT NULL;
        END IF;
    END
    $$;
    """)
    
    # Add can_manage_expenses column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='employees' AND column_name='can_manage_expenses') THEN
            ALTER TABLE employees ADD COLUMN can_manage_expenses BOOLEAN DEFAULT FALSE NOT NULL;
        END IF;
    END
    $$;
    """)


def downgrade() -> None:
    # Remove can_manage_expenses column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='employees' AND column_name='can_manage_expenses') THEN
            ALTER TABLE employees DROP COLUMN can_manage_expenses;
        END IF;
    END
    $$;
    """)
    
    # Remove can_manage_inventory column if it exists
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name='employees' AND column_name='can_manage_inventory') THEN
            ALTER TABLE employees DROP COLUMN can_manage_inventory;
        END IF;
    END
    $$;
    """)