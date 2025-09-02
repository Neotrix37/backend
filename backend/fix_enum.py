import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    print("🔍 Checking database enum values...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Start a transaction
            with conn.begin():
                # 1. Check current enum values
                result = conn.execute(text("""
                    SELECT e.enumlabel 
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid  
                    WHERE t.typname = 'paymentmethod'
                    ORDER BY e.enumsortorder;
                """))
                current_values = [row[0] for row in result]
                print("Current enum values:", current_values)

                # 2. Check values in sales table
                result = conn.execute(text("""
                    SELECT DISTINCT payment_method 
                    FROM sales 
                    WHERE payment_method IS NOT NULL;
                """))
                sales_values = [row[0] for row in result]
                print("\nValues in sales table:", sales_values)

                # 3. Add missing enum values
                missing_values = [v for v in sales_values if v not in current_values]
                
                if missing_values:
                    print("\n🔧 Adding missing enum values...")
                    for value in missing_values:
                        try:
                            conn.execute(text(
                                f"ALTER TYPE paymentmethod ADD VALUE IF NOT EXISTS '{value}';"
                            ))
                            print(f"✅ Added '{value}' to paymentmethod enum")
                        except Exception as e:
                            print(f"⚠️ Error adding '{value}': {e}")
                else:
                    print("\n✅ All values in sales table are valid enum values")

                # 4. Verify the fix
                result = conn.execute(text("""
                    SELECT e.enumlabel 
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid  
                    WHERE t.typname = 'paymentmethod'
                    ORDER BY e.enumsortorder;
                """))
                print("\n✅ Final enum values:", [row[0] for row in result])

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()