import json
import joblib
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from kafka import KafkaConsumer

# Configuration
KAFKA_TOPIC = 'transactions'
KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092']
MODEL_PATH = 'fraud_model.pkl'

def send_alert(transaction):
    sender = "security@bank-sentinel.ai"
    receiver = "admin@bank.com"
    
    subject = f"🚨 FRAUD ALERT: Transaction {transaction['transaction_id'][:8]}"
    body = f"""
    URGENT: High-Risk Transaction Detected
    --------------------------------------
    Amount: ${transaction['amount']}
    User ID: {transaction['user_id']}
    Merchant: {transaction['merchant_id']}
    
    Status: BLOCKED
    """
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        # Connect to the fake email server
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
        print("    📧 EMAIL SENT TO ADMIN!")  # <--- WE WANT TO SEE THIS
    except Exception as e:
        print(f"    ❌ EMAIL FAILED: {e}")

def main():
    print("\n📧 STARTING DETECTIVE WITH EMAIL SYSTEM v2.0...") 
    print("------------------------------------------------")
    
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        print("❌ Model not found. Run train_model.py first.")
        return

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        api_version=(0, 10, 1)  # Fix for your Kafka version
    )

    print("🕵️  Detector is watching...")

    for message in consumer:
        txn = message.value
        
        features = pd.DataFrame([{
            'amount': txn['amount'],
            'merchant_id': txn['merchant_id'],
            'is_weekend': txn['is_weekend']
        }])

        if model.predict(features)[0] == 1:
            print(f"🚨 FRAUD: ${txn['amount']}")
            send_alert(txn)  # <--- This triggers the email
        else:
            print(f"✅ Safe: ${txn['amount']}")

if __name__ == "__main__":
    main()