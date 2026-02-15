import time
import json
import random
import uuid
from kafka import KafkaProducer
from faker import Faker
import os

# Define Kafka configuration based on environment (Docker vs Local)
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', '127.0.0.1:9092')
TOPIC_NAME = 'transactions'

# Initialize Faker for synthetic data generation
fake = Faker()

def generate_transaction():
    user_id = random.randint(1000, 1100)
    merchant_id = random.randint(20, 100)
    
    # 20% chance of a high-value fraud transaction
    is_anomaly = random.random() < 0.2 
    
    if is_anomaly:
        amount = round(random.uniform(10000, 50000), 2)
        is_fraud = 1 # Force it to be fraud
    else:
        amount = round(random.uniform(10, 5000), 2)
        is_fraud = 0

    return {
        'transaction_id': str(uuid.uuid4()),
        'timestamp': time.time(),
        'user_id': user_id,
        'amount': amount,
        'currency': 'USD',
        'merchant_id': merchant_id,
        'ip_address': fake.ipv4(),
        'city': fake.city(),
        # Focus coordinates on the US East Coast (approx NY/NJ area) so they cluster nicely
        'latitude': round(random.uniform(39.0, 42.0), 6), 
        'longitude': round(random.uniform(-75.0, -73.0), 6),
        'is_weekend': 1 if time.localtime(time.time()).tm_wday >= 5 else 0, # Kept for compatibility
        'is_fraud': is_fraud 
    }

def run_producer():
    """
    Initializes Kafka Producer and streams data continuously.
    """
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(2, 5, 0) # Ensure compatibility with newer brokers
    )
    print(f"✅ Producer connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
    print("🚀 Starting transaction stream (with Geospatial Data)...")

    try:
        while True:
            transaction = generate_transaction()
            producer.send(TOPIC_NAME, transaction)
            # Print a brief log to terminal
            print(f"Sent: {transaction['transaction_id'][:8]} | ${transaction['amount']} | {transaction['city']}")
            # Slightly faster generation rate
            time.sleep(random.uniform(0.5, 1.5))
    except KeyboardInterrupt:
        print("\n🛑 Producer stopped by user.")
        producer.close()

if __name__ == '__main__':
    run_producer()