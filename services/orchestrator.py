import os
from typing import Dict, Any
from .diagnosis import DiagnosisService
from .recovery_predictor import RecoveryPredictor
from .ai_agent import AIAgent
from .guardrails import GuardrailEngine
from .razorpay_service import RazorpayService
from utils.audit_logger import AuditLogger

class WorkflowOrchestrator:
    def __init__(self):
        self.diagnosis_service = DiagnosisService()
        self.predictor = RecoveryPredictor()
        self.ai_agent = AIAgent()
        self.guardrails = GuardrailEngine()
        self.rzp_service = RazorpayService()
        
    def process_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single payment failure case through the complete pipeline.
        """
        case_id = case_data.get('case_id', 'unknown_case')
        amount = case_data.get('transaction_amount', 0.0)
        
        # 1. Verification (Implicit in Guardrails for 'already_paid')
        
        # 2. Diagnosis
        diagnosis_result = self.diagnosis_service.analyze(case_data)
        
        # 3. ML Prediction
        prediction_result = self.predictor.predict(case_data)
        recovery_prob = prediction_result.get('recovery_probability', 0.0)
        
        # Calculate Expected Recovery Value
        intervention_cost = float(os.getenv("INTERVENTION_COST", "50.0")) # Base cost
        erv = (recovery_prob * amount) - intervention_cost
        
        # 4. AI Recommendation
        ai_context = {
            **case_data,
            "diagnosis": diagnosis_result['diagnosis'],
            "diagnosis_evidence": diagnosis_result['evidence'],
            "recovery_probability": recovery_prob,
            "expected_recovery_value": erv
        }
        
        try:
            ai_recommendation = self.ai_agent.recommend_action(ai_context)
            ai_rec_dict = {
                "action": ai_recommendation.action,
                "reason": ai_recommendation.reason,
                "confidence": ai_recommendation.confidence,
                "evidence": ai_recommendation.evidence
            }
        except Exception as e:
             ai_rec_dict = {
                "action": "ESCALATE",
                "reason": f"AI Agent Failed: {e}",
                "confidence": 0.0,
                "evidence": []
             }
             
        AuditLogger.log_event(
            case_id=case_id,
            stage="AI_RECOMMENDATION",
            actor="AI_AGENT",
            decision=ai_rec_dict['action'],
            reason=ai_rec_dict['reason'],
            evidence=ai_rec_dict['evidence']
        )
        
        # 5. Guardrail Validation
        guardrail_result = self.guardrails.validate_action(case_data, ai_rec_dict, erv)
        
        AuditLogger.log_event(
            case_id=case_id,
            stage="GUARDRAIL_VALIDATION",
            actor="GUARDRAIL_ENGINE",
            decision=guardrail_result['decision'],
            reason=guardrail_result['reason'],
            evidence=guardrail_result['rules_triggered']
        )
        
        # 6. Final Action Execution
        final_decision = guardrail_result['decision']
        execution_result = None
        
        if guardrail_result['execution_permitted'] and ai_rec_dict['action'] == "SEND_PAYMENT_LINK":
            try:
                link_data = self.rzp_service.create_payment_link(
                    amount_in_inr=amount, 
                    customer_id=case_data.get('customer_id', 'unknown'), 
                    case_id=case_id
                )
                execution_result = {"status": "success", "payment_link": link_data.get('short_url')}
                
                AuditLogger.log_event(
                    case_id=case_id,
                    stage="ACTION_EXECUTION",
                    actor="SYSTEM",
                    decision="EXECUTED",
                    reason="Payment link created",
                    additional_context={"payment_link_id": link_data.get('id')}
                )
            except Exception as e:
                execution_result = {"status": "error", "message": str(e)}
                AuditLogger.log_event(
                    case_id=case_id,
                    stage="ACTION_EXECUTION",
                    actor="SYSTEM",
                    decision="FAILED",
                    reason=f"Execution error: {e}"
                )
                
        return {
            "case_id": case_id,
            "diagnosis": diagnosis_result,
            "prediction": prediction_result,
            "expected_recovery_value": erv,
            "ai_recommendation": ai_rec_dict,
            "guardrail_result": guardrail_result,
            "execution_result": execution_result
        }
