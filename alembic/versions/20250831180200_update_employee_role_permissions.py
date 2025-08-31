"""Update employee role permissions

Revision ID: 20250831180200
Revises: fe87d2d868a2
Create Date: 2025-08-31 18:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '20250831180200'
down_revision = 'fe87d2d868a2'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    bind = op.get_bind()
    if bind.engine.name == 'postgresql':
        result = bind.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = :table AND column_name = :column
                )
                """
            ),
            {'table': table_name, 'column': column_name}
        ).scalar()
        return result
    return False

def upgrade():
    # Create the enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'employeerole') THEN
                CREATE TYPE employeerole AS ENUM ('admin', 'manager', 'cashier', 'viewer');
            END IF;
        END
        $$;
    """)
    
    # Add role column if it doesn't exist
    if not column_exists('employees', 'role'):
        op.add_column('employees', 
                     sa.Column('role', 
                              sa.Enum('admin', 'manager', 'cashier', 'viewer', name='employeerole'),
                              nullable=False, 
                              server_default='cashier'))
    
    # Add is_active column if it doesn't exist
    if not column_exists('employees', 'is_active'):
        op.add_column('employees', 
                     sa.Column('is_active', 
                              sa.Boolean(), 
                              server_default='true', 
                              nullable=False))
    
    # Set role based on existing permissions if the old columns exist
    if column_exists('employees', 'is_admin'):
        op.execute("""
            UPDATE employees 
            SET role = CASE 
                WHEN is_admin = true THEN 'admin'::employeerole
                WHEN can_manage_inventory = true OR can_manage_expenses = true THEN 'manager'::employeerole
                WHEN can_sell = true THEN 'cashier'::employeerole
                ELSE 'viewer'::employeerole
            END
        """)
    
    # Drop old permission columns if they exist
    for column in ['is_admin', 'can_sell', 'can_manage_inventory', 'can_manage_expenses']:
        if column_exists('employees', column):
            op.drop_column('employees', column)

def downgrade():
    # Add back the old columns if they don't exist
    if not column_exists('employees', 'is_admin'):
        op.add_column('employees', 
                     sa.Column('is_admin', 
                              sa.BOOLEAN(), 
                              server_default=sa.text('false'), 
                              nullable=False))
    
    if not column_exists('employees', 'can_sell'):
        op.add_column('employees', 
                     sa.Column('can_sell', 
                              sa.BOOLEAN(), 
                              server_default=sa.text('true'), 
                              nullable=False))
    
    if not column_exists('employees', 'can_manage_inventory'):
        op.add_column('employees', 
                     sa.Column('can_manage_inventory', 
                              sa.BOOLEAN(), 
                              server_default=sa.text('false'), 
                              nullable=False))
    
    if not column_exists('employees', 'can_manage_expenses'):
        op.add_column('employees', 
                     sa.Column('can_manage_expenses', 
                              sa.BOOLEAN(), 
                              server_default=sa.text('false'), 
                              nullable=False))
    
    # Migrate data back if role column exists
    if column_exists('employees', 'role'):
        op.execute("""
            UPDATE employees 
            SET is_admin = (role = 'admin'::employeerole),
                can_sell = (role IN ('admin'::employeerole, 'manager'::employeerole, 'cashier'::employeerole)),
                can_manage_inventory = (role IN ('admin'::employeerole, 'manager'::employeerole)),
                can_manage_expenses = (role IN ('admin'::employeerole, 'manager'::employeerole))
        """)
    
    # Drop new columns if they exist
    if column_exists('employees', 'role'):
        op.drop_column('employees', 'role')
    
    if column_exists('employees', 'is_active'):
        op.drop_column('employees', 'is_active')
    
    # Don't drop the enum type as it might be in use by other tables or functions
