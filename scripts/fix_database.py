import os
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text

def get_alembic_config():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to alembic.ini
    alembic_ini = os.path.join(current_dir, 'alembic.ini')
    
    # Create Alembic config
    alembic_cfg = Config(alembic_ini)
    
    # Set the script location
    alembic_cfg.set_main_option('script_location', os.path.join(current_dir, 'alembic'))
    
    return alembic_cfg

def check_database_connection():
    print("\n🔍 Checking database connection...")
    try:
        from app.core.config import settings
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            print("✅ Successfully connected to the database!")
            
            # Check if alembic_version table exists
            result = conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
                """)
            )
            has_alembic_table = result.scalar()
            
            if has_alembic_table:
                print("ℹ️  Found alembic_version table")
                # Get current revision
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_rev = result.scalar()
                print(f"   Current revision: {current_rev}")
            else:
                print("ℹ️  No alembic_version table found")
                
            # List all tables
            print("\n📋 Database tables:")
            result = conn.execute(
                text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """)
            )
            tables = [row[0] for row in result]
            
            if tables:
                for table in tables:
                    print(f"- {table}")
            else:
                print("No tables found in the database.")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def fix_migrations():
    print("\n🛠️  Fixing database migrations...")
    alembic_cfg = get_alembic_config()
    
    try:
        # Get the list of migrations
        print("\n📜 Available migrations:")
        command.history(alembic_cfg)
        
        # Try to create a merge migration
        print("\n🔄 Creating merge migration...")
        command.merge(alembic_cfg, 'heads', message='merge multiple heads')
        
        # Apply migrations
        print("\n🔄 Applying migrations...")
        command.upgrade(alembic_cfg, 'head')
        
        print("\n✅ Database migrations fixed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error fixing migrations: {str(e)}")
        
        # Try to stamp the database with the latest revision
        try:
            print("\n🔄 Attempting to stamp the database with the latest revision...")
            command.stamp(alembic_cfg, 'head')
            print("✅ Successfully stamped the database with the latest revision.")
            return True
        except Exception as e2:
            print(f"❌ Failed to stamp the database: {str(e2)}")
            return False

def main():
    print("🔧 Database Migration Fix Tool 🔧")
    print("-" * 40)
    
    # Add the project root to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check database connection first
    if not check_database_connection():
        print("\n❌ Cannot proceed without a valid database connection.")
        return
    
    # Try to fix migrations
    if fix_migrations():
        print("\n✅ All done! Your database should now be in a consistent state.")
    else:
        print("\n❌ Failed to fix migrations automatically. You may need to resolve them manually.")
        print("   Check the error messages above for more information.")

if __name__ == "__main__":
    main()
