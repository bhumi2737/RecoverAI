import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.orchestrator import WorkflowOrchestrator

def print_result(name: str, res: dict):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"AI Recommendation: {res['ai_recommendation']['action']} (Confidence: {res['ai_recommendation']['confidence']})")
    print(f"Guardrail Decision: {res['guardrail_result']['decision']}")
    print(f"Guardrail Reason: {res['guardrail_result']['reason']}")
    print(f"Recovery Prob: {res['prediction']['recovery_probability']:.2f}")
    print(f"Expected Value: {res['expected_recovery_value']:.2f}")
    if res['execution_result']:
        print(f"Execution: {res['execution_result']}")

def test_workflow():
    orchestrator = WorkflowOrchestrator()
    
    # Base case template (matches features used in training)
    base_case = {
        "transaction_id": "test_txn",
        "customer_id": "test_cust",
        "transaction_amount": 1000.0,
        "payment_status": "failed",
        "failure_reason": "network_error",
        "payment_method": "credit_card",
        "successful_payments": 15,
        "failed_payments": 1,
        "total_customer_spend": 15000.0,
        "average_order_value": 1000.0,
        "previous_recovery_attempts": 0,
        "previous_recovery_success": 0,
        "days_since_last_purchase": 5,
        "customer_tenure_days": 300,
        "already_paid": False,
        "contact_attempts": 0,
        "previous_action": None
    }
    
    # Test 1: Normal recoverable payment
    case1 = dict(base_case)
    case1["case_id"] = "case_test_1"
    res1 = orchestrator.process_case(case1)
    print_result("Test 1 - Normal recoverable payment", res1)
    assert res1['guardrail_result']['decision'] == "ALLOW", "Test 1 Failed"

    # Test 2: Maximum recovery attempts
    case2 = dict(base_case)
    case2["case_id"] = "case_test_2"
    case2["previous_recovery_attempts"] = 2
    res2 = orchestrator.process_case(case2)
    print_result("Test 2 - Maximum recovery attempts", res2)
    assert res2['guardrail_result']['decision'] == "BLOCK", "Test 2 Failed"
    
    # Test 3: Customer already paid
    case3 = dict(base_case)
    case3["case_id"] = "case_test_3"
    case3["already_paid"] = True
    res3 = orchestrator.process_case(case3)
    print_result("Test 3 - Customer already paid", res3)
    assert res3['guardrail_result']['decision'] == "STOP", "Test 3 Failed"
    
    # Test 4: Low AI confidence
    # We simulate this by overriding the AI Agent's recommendation via a mock
    # since we can't easily force the LLM to output low confidence for a good case.
    class MockAIAgentLowConfidence:
        def recommend_action(self, case_info):
            from services.ai_agent import AIActionRecommendation
            return AIActionRecommendation(
                action="SEND_PAYMENT_LINK",
                reason="Forced low confidence",
                confidence=0.2, # Below 0.6
                evidence=[]
            )
            
    case4 = dict(base_case)
    case4["case_id"] = "case_test_4"
    orchestrator.ai_agent = MockAIAgentLowConfidence()
    res4 = orchestrator.process_case(case4)
    print_result("Test 4 - Low AI confidence", res4)
    assert res4['guardrail_result']['decision'] == "ESCALATE", "Test 4 Failed"
    
    # Restore real AI Agent
    from services.ai_agent import AIAgent
    orchestrator.ai_agent = AIAgent()
    
    # Test 5: High-value transaction
    case5 = dict(base_case)
    case5["case_id"] = "case_test_5"
    case5["transaction_amount"] = 25000.0 # Above threshold of 10000
    res5 = orchestrator.process_case(case5)
    print_result("Test 5 - High-value transaction", res5)
    assert res5['guardrail_result']['decision'] == "REQUIRE_APPROVAL", "Test 5 Failed"
    
    # Test 6: Low probability case
    case6 = dict(base_case)
    case6["case_id"] = "case_test_6"
    case6["failure_reason"] = "suspected_fraud"
    res6 = orchestrator.process_case(case6)
    print_result("Test 6 - Low probability case", res6)
    
    print("\n✅ All 6 tests passed successfully!")

if __name__ == "__main__":
    test_workflow()
