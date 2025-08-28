import os
import sys
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.product import Product
from app.core.config import settings

def update_categories():
    # New categories with (name, description)
    NEW_CATEGORIES = [
        ('Alimentos', 'Produtos alimentícios em geral'),
        ('Bebidas', 'Bebidas em geral'),
        ('Limpeza', 'Produtos de limpeza'),
        ('Higiene', 'Produtos de higiene pessoal'),
        ('Congelados', 'Produtos congelados'),
        ('Mercearia', 'Produtos de mercearia em geral'),
        ('Padaria', 'Produtos de padaria'),
        ('Hortifruti', 'Frutas, legumes e verduras'),
        ('Açougue', 'Carnes em geral'),
        ('Laticínios', 'Leite e derivados'),
        ('Outros', 'Outros tipos de produtos')
    ]
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with Session(engine) as session:
            # First, set all products' category_id to NULL
            session.execute(
                update(Product).values(category_id=None)
            )
            
            # Then delete all existing categories
            session.execute(Category.__table__.delete())
            print("🗑️  Removed existing categories.")
                
            # Add new categories
            for name, description in NEW_CATEGORIES:
                category = Category(name=name, description=description)
                session.add(category)
            
            session.commit()
            print(f"✅ Successfully added {len(NEW_CATEGORIES)} new categories:")
            for name, _ in NEW_CATEGORIES:
                print(f"   - {name}")
            
            print("\n⚠️  Note: All products have been set to have no category. "
                  "Please update their categories as needed.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    update_categories()
