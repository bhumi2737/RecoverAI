import pytest
import os
from services.recovery_predictor import RecoveryPredictor

def test_recovery_predictor_loads_model():
    predictor = RecoveryPredictor()
    
    case_data = {
        'customer_tenure_days': 100,
        'successful_payments': 5,
        'failed_payments': 1,
        'total_customer_spend': 5000.0,
        'average_order_value': 1000.0,
        'previous_recovery_attempts': 0,
        'previous_recovery_success': 0,
        'days_since_last_purchase': 5,
        'failure_reason': 'insufficient_funds',
        'payment_method': 'credit_card'
    }
    
    res = predictor.predict(case_data)
    assert 'recovery_probability' in res
    assert 'model_version' in res
    assert 0.0 <= res['recovery_probability'] <= 1.0
