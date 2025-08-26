"""remove barcode from products

Revision ID: remove_barcode_from_products
Revises: remove_unused_product_columns
Create Date: 2025-08-26 07:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_barcode_from_products'
down_revision = 'remove_unused_product_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove the barcode column
    op.drop_column('products', 'barcode')


def downgrade() -> None:
    # Add the barcode column back (nullable for safety)
    op.add_column('products', 
        sa.Column('barcode', sa.String(length=50), nullable=True, index=True, unique=True)
    )
    
    # If you need to create an index separately:
    # op.create_index('idx_products_barcode', 'products', ['barcode'], unique=True)
