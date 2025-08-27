"""add is_active to users

Revision ID: 1234567890ab
Revises: 002c68f0fdd9
Create Date: 2025-08-27 06:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '002c68f0fdd9'
branch_labels = None
depends_on = None

def upgrade():
    # Add is_active column with default True
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))

def downgrade():
    # Remove the is_active column
    op.drop_column('users', 'is_active')
