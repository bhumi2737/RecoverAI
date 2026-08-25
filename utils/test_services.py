import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongo import MongoDB
from database.repositories import CaseRepository, AuditRepository
from utils.audit_logger import AuditLogger
from services.ai_agent import AIAgent
from services.razorpay_service import RazorpayService

def test_services():
    print("Testing MongoDB Connection...")
    client = MongoDB.get_client()
    if client:
        print("[SUCCESS] MongoDB connection successful.")
    else:
        print("[FAILED] MongoDB connection failed.")
        
    print("\nTesting Repositories...")
    case_data = {
        "customer_id": "test_cust_123",
        "transaction_amount": 1500.0,
        "payment_status": "failed",
        "failure_reason": "insufficient_funds"
    }
    try:
        case_id = CaseRepository.create_case(case_data)
        print(f"[SUCCESS] Case created with ID: {case_id}")
        
        fetched_case = CaseRepository.get_case(case_id)
        if fetched_case:
             print("[SUCCESS] Case fetched successfully.")
        else:
             print("[FAILED] Failed to fetch case.")
             
        log_id = AuditLogger.log_event(
            case_id=case_id,
            stage="TEST",
            actor="SYSTEM",
            decision="ALLOWED",
            reason="Testing audit logger",
            evidence=["Test evidence"]
        )
        print(f"[SUCCESS] Audit log created with ID: {log_id}")
        
    except Exception as e:
         print(f"[FAILED] Repository test failed: {e}")

    print("\nTesting AI Agent...")
    try:
        agent = AIAgent()
        case_info = {
            "recovery_probability": 0.85,
            "previous_recovery_attempts": 0,
            "failure_reason": "insufficient_funds"
        }
        recommendation = agent.recommend_action(case_info)
        print(f"[SUCCESS] AI Recommendation generated: {recommendation.action}")
        print(f"   Reason: {recommendation.reason}")
    except Exception as e:
        print(f"[FAILED] AI Agent test failed: {e}")
        
    print("\nTesting Razorpay Service (Demo Mode)...")
    try:
        rzp_service = RazorpayService()
        link = rzp_service.create_payment_link(1500.0, "test_cust_123", "test_case_id")
        print(f"[SUCCESS] Payment link generated: {link['short_url']}")
        status = rzp_service.check_payment_status(link['id'])
        print(f"[SUCCESS] Payment status checked: {status}")
    except Exception as e:
        print(f"[FAILED] Razorpay test failed: {e}")

if __name__ == "__main__":
    test_services()
