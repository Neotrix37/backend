from alembic.config import Config
from alembic import command
import os

def fix_migrations():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to alembic.ini
    alembic_ini = os.path.join(current_dir, 'alembic.ini')
    
    # Create Alembic config
    alembic_cfg = Config(alembic_ini)
    
    # Set the script location
    alembic_cfg.set_main_option('script_location', os.path.join(current_dir, 'alembic'))
    
    print("Creating merge migration...")
    try:
        # Create a merge migration
        command.merge(alembic_cfg, 'heads', message='merge multiple heads')
        print("Merge migration created successfully!")
        
        # Upgrade to the latest migration
        print("\nApplying migrations...")
        command.upgrade(alembic_cfg, 'head')
        print("Migrations applied successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTrying to resolve by stamping the latest migration...")
        try:
            # Stamp the database with the latest revision
            command.stamp(alembic_cfg, 'head')
            print("Successfully stamped the database with the latest migration.")
        except Exception as e2:
            print(f"Failed to stamp the database: {str(e2)}")
            print("\nPlease check your migration files in the 'alembic/versions' directory.")

if __name__ == '__main__':
    fix_migrations()
