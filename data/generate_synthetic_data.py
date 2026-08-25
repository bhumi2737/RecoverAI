import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(num_records=500):
    data = []
    
    reasons = [
        "insufficient_funds", 
        "card_declined", 
        "expired_card", 
        "suspected_fraud", 
        "network_error", 
        "authentication_failed"
    ]
    
    payment_methods = ["credit_card", "debit_card", "upi", "netbanking"]

    for i in range(num_records):
        customer_id = f"cust_{np.random.randint(1000, 9999)}"
        transaction_id = f"txn_{np.random.randint(10000, 99999)}"
        
        # Base features
        transaction_amount = round(np.random.uniform(50, 25000), 2)
        failure_reason = np.random.choice(reasons, p=[0.4, 0.2, 0.15, 0.05, 0.1, 0.1])
        payment_method = np.random.choice(payment_methods, p=[0.4, 0.3, 0.2, 0.1])
        
        # Customer history
        customer_tenure_days = np.random.randint(1, 1000)
        successful_payments = np.random.randint(0, 50)
        failed_payments = np.random.randint(1, 10) # At least 1 (this one)
        
        total_customer_spend = successful_payments * round(np.random.uniform(100, 5000), 2)
        average_order_value = total_customer_spend / successful_payments if successful_payments > 0 else 0
        
        previous_recovery_attempts = np.random.randint(0, 3)
        previous_recovery_success = np.random.randint(0, previous_recovery_attempts + 1) if previous_recovery_attempts > 0 else 0
        
        days_since_last_purchase = np.random.randint(1, customer_tenure_days + 1)
        
        # Target variable generation (with some logical rules)
        # Base probability
        recovery_prob = 0.5
        
        if failure_reason in ["insufficient_funds", "network_error"]:
            recovery_prob += 0.2
        if failure_reason == "suspected_fraud":
            recovery_prob -= 0.4
            
        if successful_payments > 10:
            recovery_prob += 0.15
            
        if failed_payments > 5:
            recovery_prob -= 0.15
            
        if previous_recovery_success > 0:
            recovery_prob += 0.1
            
        # Ensure prob is between 0.05 and 0.95
        recovery_prob = max(0.05, min(0.95, recovery_prob))
        
        recovered = np.random.binomial(1, recovery_prob)
        
        data.append({
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "transaction_amount": transaction_amount,
            "payment_status": "failed",
            "failure_reason": failure_reason,
            "payment_method": payment_method,
            "successful_payments": successful_payments,
            "failed_payments": failed_payments,
            "total_customer_spend": total_customer_spend,
            "average_order_value": average_order_value,
            "previous_recovery_attempts": previous_recovery_attempts,
            "previous_recovery_success": previous_recovery_success,
            "days_since_last_purchase": days_since_last_purchase,
            "customer_tenure_days": customer_tenure_days,
            "recovered": recovered
        })

    df = pd.DataFrame(data)
    
    # Save to CSV
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "payment_recovery_data.csv")
    df.to_csv(output_file, index=False)
    print(f"Generated {num_records} synthetic records and saved to {output_file}")
    
    return df

if __name__ == "__main__":
    generate_synthetic_data(1000)
