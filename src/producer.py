import time
import json
import random
from kafka import KafkaProducer
from faker import Faker

KAFKA_TOPIC = 'transactions'
# REMEMBER: Use '127.0.0.1:9092' because of the Windows/Docker bug
KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092']

fake = Faker()

def get_transaction():
    """Generates a transaction with occasional FRAUD patterns."""
    user_id = random.randint(1000, 1050)
    
    # 50% chance of being Fraud for this simulation
    is_fraud = 1 if random.random() < 0.5 else 0
    
    # Logic: Fraudsters spend BIG or use weird locations
    if is_fraud:
        amount = round(random.uniform(2000.00, 9000.00), 2)  # High Amount
        merchant_id = random.randint(900, 999)               # Suspicious Merchants
    else:
        amount = round(random.uniform(5.00, 500.00), 2)      # Normal Amount
        merchant_id = random.randint(1, 50)                  # Trusted Merchants

    return {
        "transaction_id": fake.uuid4(),
        "timestamp": time.time(),
        "user_id": user_id,
        "amount": amount,
        "currency": "USD",
        "merchant_id": merchant_id,
        "location": fake.city(),
        "ip_address": fake.ipv4(),
        "is_weekend": 1 if time.localtime().tm_wday >= 5 else 0,
        "is_fraud": is_fraud  # <--- NEW LABEL
    }

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        api_version=(0, 10, 1)  # <--- ADD THIS LINE
    )

    try:
        while True:
            txn = get_transaction()
            producer.send(KAFKA_TOPIC, txn)
            
            # Print Fraud in RED (if your terminal supports it) or just mark it
            status = "🚨 FRAUD" if txn['is_fraud'] else "✅ LEGIT"
            print(f"Sent: {status} | User {txn['user_id']} | ${txn['amount']}")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        producer.close()

if __name__ == "__main__":
    main()