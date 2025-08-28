import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import subprocess

def fix_alembic_version():
    # Get database URL from environment or config
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        # Connect to the database
        engine = create_engine(db_url)
        
        # SQL to update the alembic version
        update_sql = """
        -- First, check if the table exists
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version') THEN
                -- Update to the correct version
                UPDATE alembic_version SET version_num = '3901e0af53cd';
                RAISE NOTICE 'Updated alembic_version to 3901e0af53cd';
            ELSE
                -- Create the table if it doesn't exist
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL
                );
                INSERT INTO alembic_version (version_num) VALUES ('3901e0af53cd');
                RAISE NOTICE 'Created alembic_version table with version 3901e0af53cd';
            END IF;
        END $$;
        """
        
        with engine.connect() as conn:
            # Execute the SQL
            conn.execute(text(update_sql))
            conn.commit()
            
        print("✅ Successfully fixed the alembic version table.")
        
        # Apply the migrations
        print("\n🔨 Applying migrations...")
        subprocess.run(["alembic", "stamp", "head"], check=True)
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        print("\n✅ All migrations applied successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fix_alembic_version()
