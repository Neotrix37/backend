"""remove_unused_product_columns

Revision ID: remove_unused_product_columns
Revises: add_salary_to_users
Create Date: 2025-08-26 09:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Identificação da revisão
revision = 'remove_unused_product_columns'
down_revision = 'add_salary_to_users'
branch_labels = None
depends_on = None

def upgrade():
    # Remover as colunas desnecessárias
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('wholesale_price')
        batch_op.drop_column('is_service')
        batch_op.drop_column('max_stock')
    
    print("✅ Colunas removidas com sucesso: wholesale_price, is_service, max_stock")

def downgrade():
    # Adicionar as colunas novamente para rollback
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wholesale_price', sa.Numeric(10, 2), nullable=True))
        batch_op.add_column(sa.Column('is_service', sa.Boolean(), server_default=sa.text('false'), nullable=False))
        batch_op.add_column(sa.Column('max_stock', sa.INTEGER(), nullable=True))
    
    print("✅ Colunas readicionadas para rollback: wholesale_price, is_service, max_stock")
