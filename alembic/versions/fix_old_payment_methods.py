"""fix_old_payment_methods

Revision ID: fix_old_payment_methods
Revises: 8f328e013490
Create Date: 2025-08-28 11:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'fix_old_payment_methods'
down_revision = '8f328e013490'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Check if sales table exists
    table_exists = conn.execute(
        text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'sales'
        );
        """)
    ).scalar()
    
    if not table_exists:
        return
    
    # Get current enum values
    enum_values = conn.execute(
        text("""
        SELECT e.enumlabel 
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid  
        WHERE t.typname = 'paymentmethod';
        """)
    ).scalars().all()
    
    print(f"Current enum values: {enum_values}")
    
    # Define the updates we want to make
    updates = [
        ('CARTAO_CREDITO', 'CARTAO_POS'),
        ('CARTAO_DEBITO', 'CARTAO_POS'),
        ('CREDITO', 'CARTAO_POS'),
        ('DEBITO', 'CARTAO_POS'),
        ('PIX', 'TRANSFERENCIA'),
        ('BOLETO', 'TRANSFERENCIA'),
    ]
    
    # Execute updates one by one with error handling
    for old_val, new_val in updates:
        if old_val in enum_values and new_val in enum_values:
            try:
                print(f"Updating {old_val} to {new_val}")
                conn.execute(
                    text("""
                    UPDATE sales 
                    SET payment_method = :new_val
                    WHERE payment_method = :old_val
                    """),
                    {'new_val': new_val, 'old_val': old_val}
                )
                # Commit after each successful update
                conn.execute(text("COMMIT"))
            except Exception as e:
                print(f"Error updating {old_val} to {new_val}: {e}")
                conn.execute(text("ROLLBACK"))
                continue

def downgrade():
    # No need to downgrade as this is a data fix
    pass
