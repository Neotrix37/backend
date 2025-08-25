import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

def test_db_connection():
    print("Testing database connection...")
    
    # Import settings to get database URL
    from app.core.config import settings
    
    db_url = settings.DATABASE_URL
    print(f"Connecting to: {db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as connection:
            print("✅ Successfully connected to the database!")
            
            # List all tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if tables:
                print("\n📋 Found tables:")
                for table in tables:
                    print(f"- {table}")
            else:
                print("\nℹ️ No tables found in the database.")
                
    except Exception as e:
        print(f"❌ Error connecting to the database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Add the project root to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_db_connection()
