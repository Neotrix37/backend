import sys
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User, UserRole, get_password_hash

def create_admin_user(
    db: Session, 
    username: str, 
    password: str, 
    email: Optional[str] = None,
    full_name: Optional[str] = "Admin User"
) -> User:
    """Create an admin user if it doesn't exist"""
    # Check if admin user already exists
    admin = db.query(User).filter(User.username == username).first()
    if admin:
        print(f"Admin user '{username}' already exists.")
        return admin
    
    # Create new admin user
    admin = User(
        username=username,
        email=email,
        full_name=full_name,
        role=UserRole.ADMIN,
        is_superuser=True,
        is_active=True
    )
    admin.hashed_password = get_password_hash(password)
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"Created admin user: {username}")
    return admin

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m scripts.create_admin <username> <password> [email] [full_name]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else f"{username}@example.com"
    full_name = sys.argv[4] if len(sys.argv) > 4 else "Admin User"
    
    db = SessionLocal()
    try:
        admin = create_admin_user(db, username, password, email, full_name)
        print(f"Admin user created successfully!")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Role: {admin.role}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
