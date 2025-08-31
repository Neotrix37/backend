import sys
import os
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import necessary modules
from app.core.database import engine, SessionLocal
from app.models.base import Base
from app.models.product import Product
from app.schemas.product import ProductCreate

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_sample_product():
    # Create a new database session
    db = SessionLocal()
    
    try:
        # Create a sample product
        product_data = ProductCreate(
            codigo="PROD001",
            nome="Produto de Teste",
            descricao="Descrição do produto de teste",
            preco_compra=10.50,
            preco_venda=19.90,
            estoque=100,
            estoque_minimo=10,
            venda_por_peso=False,
            category_id=None  # You can set this to an existing category ID if needed
        )
        
        # Create and add the product
        product = Product(
            codigo=product_data.codigo,
            nome=product_data.nome,
            descricao=product_data.descricao,
            preco_compra=product_data.preco_compra,
            preco_venda=product_data.preco_venda,
            estoque=product_data.estoque,
            estoque_minimo=product_data.estoque_minimo,
            venda_por_peso=product_data.venda_por_peso,
            category_id=product_data.category_id,
            is_active=True
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        print(f"Produto criado com sucesso! ID: {product.id}")
        print(f"Nome: {product.nome}")
        print(f"Código: {product.codigo}")
        print(f"Preço de venda: R$ {product.preco_venda:.2f}")
        print(f"Estoque: {product.estoque}")
        
        return product
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar produto: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_product()
