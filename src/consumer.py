import json
import time
from kafka import KafkaConsumer
from sqlalchemy import text
from db_utils import create_tables, get_engine

# USE THE WORKING PORT 6543
KAFKA_TOPIC = 'transactions'
KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092']

def main():
    print("⏳ Starting Consumer...")
    
    # 1. Initialize Database
    create_tables()
    engine = get_engine()
    print("✅ Database tables checked/created.")
    
    # 2. Connect to Kafka
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        api_version=(2, 5, 0)  # Fix for your Kafka version
    )

    print(f"✅ Consumer listening on topic: {KAFKA_TOPIC}")

    # 3. Process Messages
    for message in consumer:
        txn = message.value
        
        # We use a context manager to handle the connection safely
        with engine.connect() as conn:
            # UPDATE: Add "ON CONFLICT DO NOTHING" to handle duplicates gracefully
            insert_query = text("""
                INSERT INTO transactions (
                    transaction_id, timestamp, user_id, amount, currency, 
                    merchant_id, city, ip_address, latitude, longitude, is_weekend, is_fraud
                ) VALUES (
                    :transaction_id, :timestamp, :user_id, :amount, :currency, 
                    :merchant_id, :city, :ip_address, :latitude, :longitude, :is_weekend, :is_fraud
                ) ON CONFLICT (transaction_id) DO NOTHING
            """)
            
            conn.execute(insert_query, txn)
            conn.commit()
            
            # Visual feedback
            status = "🚨 FRAUD" if txn.get('is_fraud') == 1 else "💾 Saved"
            print(f"{status}: {txn['transaction_id'][:5]}... | ${txn['amount']}")

if __name__ == "__main__":
    main()