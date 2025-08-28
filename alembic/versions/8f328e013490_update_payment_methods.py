"""update_payment_methods

Revision ID: 8f328e013490
Revises: c846f4468a81
Create Date: 2025-08-28 11:19:24.240169

"""
from typing import Sequence, Union, List, Tuple

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '8f328e013490'
down_revision: Union[str, None] = 'c846f4468a81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def get_enum_values(conn, enum_name: str) -> List[str]:
    """Get the current values of an enum type"""
    result = conn.execute(
        text("""
        SELECT e.enumlabel 
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        WHERE t.typname = :enum_name
        ORDER BY e.enumsortorder;
        """),
        {'enum_name': enum_name}
    )
    return [row[0] for row in result]

def upgrade() -> None:
    conn = op.get_bind()
    
    # First, handle any NULL product_id values in sale_items
    conn.execute(
        text("""
            UPDATE sale_items 
            SET product_id = (SELECT MIN(id) FROM products)
            WHERE product_id IS NULL
        """)
    )
    
    # Handle the foreign key constraint changes
    op.drop_constraint(op.f('sale_items_product_id_fkey'), 'sale_items', type_='foreignkey')
    op.alter_column('sale_items', 'product_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'sale_items', 'products', ['product_id'], ['id'])

    # Get current enum values
    current_values = get_enum_values(conn, 'paymentmethod')
    
    # Define the mapping from old to new values
    value_mapping = {
        'CREDITO': 'CARTAO',
        'DEBITO': 'CARTAO',
        'PIX': 'TRANSFERENCIA'
    }
    
    # Add new enum values if they don't exist
    new_values = [
        'MPESA', 'EMOLA', 'MILLENNIUM', 'BCI', 
        'STANDARD_BANK', 'ABSA_BANK', 'LETSHEGO', 'MYBUCKS'
    ]
    
    for value in new_values:
        if value not in current_values:
            try:
                conn.execute(text(f"ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS '{value}'"))
            except Exception as e:
                print(f"Could not add value {value} to enum: {e}")
    
    # Update existing data to use new values
    for old_val, new_val in value_mapping.items():
        if old_val in current_values and new_val in current_values + new_values:
            try:
                conn.execute(
                    text("""
                        UPDATE sales 
                        SET payment_method = :new_val
                        WHERE payment_method = :old_val
                    """),
                    {'new_val': new_val, 'old_val': old_val}
                )
            except Exception as e:
                print(f"Could not update {old_val} to {new_val}: {e}")

def downgrade() -> None:
    conn = op.get_bind()
    
    # Map new values back to old values
    value_mapping = {
        'CARTAO': 'CREDITO',
        'TRANSFERENCIA': 'PIX'
    }
    
    # Update data back to old values
    for new_val, old_val in value_mapping.items():
        try:
            conn.execute(
                text("""
                    UPDATE sales 
                    SET payment_method = :old_val
                    WHERE payment_method = :new_val
                """),
                {'new_val': new_val, 'old_val': old_val}
            )
        except Exception as e:
            print(f"Could not update {new_val} to {old_val}: {e}")
    
    # Handle the foreign key constraint rollback
    op.drop_constraint('sale_items_product_id_fkey', 'sale_items', type_='foreignkey')
    op.alter_column('sale_items', 'product_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key('sale_items_product_id_fkey', 'sale_items', 'products', 
                         ['product_id'], ['id'], ondelete='SET NULL')
