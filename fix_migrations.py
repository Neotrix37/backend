#!/usr/bin/env python3
"""
Script to fix multiple head revisions in Alembic migrations.
Run this script to create a merge migration that will resolve the branching.
"""
import os
import sys
from logging.config import fileConfig

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_alembic_config():
    """Get the Alembic configuration."""
    config = Config("alembic.ini")
    return config

def get_current_heads():
    """Get the current migration heads."""
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)
    return script.get_heads()

def create_merge_migration():
    """Create a merge migration to resolve multiple heads."""
    print("Creating merge migration...")
    config = get_alembic_config()
    
    # Get current heads
    heads = get_current_heads()
    if len(heads) <= 1:
        print("No multiple heads to merge. Current heads:", heads)
        return
        
    print(f"Found {len(heads)} heads to merge: {', '.join(heads)}")
    
    # Create merge revision
    command.merge(
        config=config,
        revisions=heads,
        message="merge multiple heads",
        branch_label="merge_heads"
    )
    
    print("Merge migration created successfully.")
    print("Run 'alembic upgrade head' to apply the merge migration.")

def main():
    """Main function to run the migration fix."""
    print("Alembic Migration Fix Tool")
    print("=" * 30)
    
    # Show current heads
    heads = get_current_heads()
    print(f"Current migration heads: {', '.join(heads) if heads else 'None'}")
    
    if len(heads) > 1:
        create_merge_migration()
    else:
        print("No multiple heads detected. Nothing to merge.")

if __name__ == "__main__":
    main()
