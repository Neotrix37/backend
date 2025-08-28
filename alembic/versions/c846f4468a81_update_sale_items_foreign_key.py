"""update_sale_items_foreign_key

Revision ID: c846f4468a81
Revises: 070e1c583426
Create Date: 2025-08-28 08:21:40.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c846f4468a81'
down_revision = '070e1c583426'
branch_labels = None
depends_on = None


def upgrade():
    # Remover a restrição de chave estrangeira existente
    op.drop_constraint('sale_items_product_id_fkey', 'sale_items', type_='foreignkey')
    
    # Recriar a coluna permitindo valores nulos
    op.alter_column('sale_items', 'product_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    
    # Recriar a chave estrangeira com ondelete='SET NULL'
    op.create_foreign_key(
        'sale_items_product_id_fkey',
        'sale_items', 'products',
        ['product_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade():
    # Reverter as alterações
    op.drop_constraint('sale_items_product_id_fkey', 'sale_items', type_='foreignkey')
    # Primeiro precisamos garantir que não há valores nulos antes de alterar para NOT NULL
    op.execute("UPDATE sale_items SET product_id = 0 WHERE product_id IS NULL")
    op.alter_column('sale_items', 'product_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)
    op.create_foreign_key(
        'sale_items_product_id_fkey',
        'sale_items', 'products',
        ['product_id'], ['id']
    )
