import sqlalchemy
from sqlalchemy import create_engine, text

def get_engine():
    # Format: postgresql://user:password@localhost:port/database
    return create_engine('postgresql://admin:password@localhost:6543/fraud_db')

def create_tables():
    """Creates the necessary tables if they don't exist."""
    engine = get_engine()
    
    # We use raw SQL for clarity and control
    # ... inside create_tables() function ...
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR(50) PRIMARY KEY,
        timestamp FLOAT,
        user_id INT,
        amount FLOAT,
        currency VARCHAR(10),
        merchant_id INT,
        location VARCHAR(100),
        ip_address VARCHAR(20),
        is_weekend INT,
        is_fraud INT      -- <--- ADDED THIS COLUMN
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("✅ Database tables checked/created.")

if __name__ == "__main__":
    # Test the connection when running this file directly
    try:
        create_tables()
        print("🚀 Database connection successful!")
    except Exception as e:
        print(f"❌ Database error: {e}")