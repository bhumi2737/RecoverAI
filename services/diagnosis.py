from typing import Dict, Any, Tuple, List

class DiagnosisService:
    """Deterministic diagnosis layer for analyzing case history."""
    
    @staticmethod
    def analyze(case_data: Dict[str, Any]) -> Dict[str, Any]:
        evidence = []
        score = 0.0
        
        failure_reason = case_data.get('failure_reason', '')
        succ_payments = case_data.get('successful_payments', 0)
        failed_payments = case_data.get('failed_payments', 1)
        prev_attempts = case_data.get('previous_recovery_attempts', 0)
        
        # Analyze Failure Reason
        if failure_reason in ['network_error', 'insufficient_funds']:
            evidence.append(f"Temporary failure reason ({failure_reason}) suggests high likelihood of recovery.")
            score += 0.4
        elif failure_reason == 'suspected_fraud':
            evidence.append(f"High risk failure reason ({failure_reason}).")
            score -= 0.5
        else:
            evidence.append(f"Standard failure reason ({failure_reason}).")
            
        # Analyze Payment History
        if succ_payments > 5 and failed_payments <= 2:
            evidence.append("Strong history of successful payments.")
            score += 0.3
        elif failed_payments > succ_payments and failed_payments > 3:
            evidence.append("History of repeated payment failures.")
            score -= 0.3
            
        # Analyze Recovery History
        if prev_attempts > 0:
            evidence.append(f"Previous recovery attempts ({prev_attempts}) observed.")
            score -= 0.2 * prev_attempts
            
        # Determine Diagnosis
        if score >= 0.5:
            diagnosis = "Likely Recoverable"
            confidence = min(0.95, score)
        elif score <= -0.2:
            diagnosis = "High Risk / Unlikely"
            confidence = min(0.9, abs(score))
        else:
            diagnosis = "Requires Standard Intervention"
            confidence = 0.6
            
        return {
            "diagnosis": diagnosis,
            "confidence": round(confidence, 2),
            "evidence": evidence
        }
