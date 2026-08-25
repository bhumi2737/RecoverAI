import pytest
import os
from services.orchestrator import WorkflowOrchestrator
from services.ai_agent import AIActionRecommendation

def test_orchestrator_mocked(mocker):
    # Mocking external calls in AI Agent
    mock_rec = AIActionRecommendation(
        action="SEND_PAYMENT_LINK",
        reason="Mock reason",
        confidence=0.85,
        evidence=["Mock evidence"]
    )
    mocker.patch('services.ai_agent.AIAgent.recommend_action', return_value=mock_rec)
    
    os.environ['INTERVENTION_COST'] = '50.0'
    os.environ['DEMO_MODE'] = 'True'
    
    orchestrator = WorkflowOrchestrator()
    
    case_data = {
        'transaction_amount': 1000.0,
        'customer_tenure_days': 100,
        'successful_payments': 5,
        'failed_payments': 1,
        'total_customer_spend': 5000.0,
        'average_order_value': 1000.0,
        'previous_recovery_attempts': 0,
        'previous_recovery_success': 0,
        'days_since_last_purchase': 5,
        'failure_reason': 'insufficient_funds',
        'payment_method': 'credit_card',
        'already_paid': False,
        'contact_attempts': 0
    }
    
    result = orchestrator.process_case(case_data)
    
    assert 'diagnosis' in result
    assert 'prediction' in result
    assert 'ai_recommendation' in result
    assert 'guardrail_result' in result
    assert 'execution_result' in result
    
    assert result['ai_recommendation']['action'] == 'SEND_PAYMENT_LINK'
    assert result['guardrail_result']['decision'] == 'ALLOW'
