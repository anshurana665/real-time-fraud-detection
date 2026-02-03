import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from db_utils import get_engine

def load_data():
    """Fetch all transaction data from the database."""
    print("⏳ Loading data from Postgres...")
    engine = get_engine()
    
    # We only select the numerical features for this first version
    # (amount, merchant_id, is_weekend)
    query = "SELECT amount, merchant_id, is_weekend, is_fraud FROM transactions"
    
    df = pd.read_sql(query, engine)
    print(f"✅ Loaded {len(df)} transactions.")
    return df

def train_model():
    df = load_data()

    # --- THE FIX IS HERE ---
    # 1. Fill missing values with 0 (Safe) and force conversion to Integer
    df['is_fraud'] = df['is_fraud'].fillna(0).astype(int)
    
    # 2. Prepare Features (X) and Target (y)
    X = df[['amount', 'merchant_id', 'is_weekend']]
    y = df['is_fraud']
    
    # Debug: Check if we actually have both classes
    print(f"DEBUG: Labels found: {y.unique()}")
    if len(y.unique()) < 2:
        print("⚠️ WARNING: Only one class found (all 0 or all 1). Model needs both to learn!")
        # We proceed anyway, but the report will look weird
        
    # 3. Split into Training (80%) and Testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"🧠 Training on {len(X_train)} rows...")

    # 4. Initialize the Model
    model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)

    # 5. Train
    model.fit(X_train, y_train)

    # 6. Evaluate
    print("\n📊 Model Evaluation:")
    predictions = model.predict(X_test)
    
    # Handle case where test set might be too small or single-class
    try:
        print(classification_report(y_test, predictions))
    except Exception as e:
        print(f"Could not generate full report (likely not enough fraud in test set): {e}")
    
    # 7. Save the Model
    joblib.dump(model, 'fraud_model.pkl')
    print("💾 Model saved to 'fraud_model.pkl'")

if __name__ == "__main__":
    train_model()