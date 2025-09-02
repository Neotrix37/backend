import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    try:
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Check current payment methods
            print("Current payment methods in use:")
            result = conn.execute(text("""
                SELECT payment_method, COUNT(*) as count 
                FROM sales 
                GROUP BY payment_method 
                ORDER BY count DESC
            """))
            for row in result:
                print(f"{row.payment_method}: {row.count}")

            # Check for CARTAO_CREDITO
            result = conn.execute(
                text("SELECT COUNT(*) as count FROM sales WHERE payment_method = 'CARTAO_CREDITO'")
            )
            count = result.scalar()
            print(f"\nFound {count} entries with CARTAO_CREDITO")

            if count > 0:
                update = input("\nUpdate CARTAO_CREDITO to CARTAO_POS? (y/n): ")
                if update.lower() == 'y':
                    conn.execute(text("""
                        UPDATE sales 
                        SET payment_method = 'CARTAO_POS'
                        WHERE payment_method = 'CARTAO_CREDITO'
                    """))
                    conn.commit()
                    print("✅ Updated CARTAO_CREDITO to CARTAO_POS")

    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    main()