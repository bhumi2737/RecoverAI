from database.repositories import AuditRepository
from datetime import datetime
from typing import Optional, Dict, Any, List

class AuditLogger:
    @staticmethod
    def log_event(
        case_id: str,
        stage: str,
        actor: str,
        decision: str,
        reason: str,
        evidence: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Logs an event to the audit trail.
        
        :param case_id: ID of the recovery case
        :param stage: e.g., 'DETECTION', 'AI_RECOMMENDATION', 'GUARDRAIL_VALIDATION'
        :param actor: e.g., 'SYSTEM', 'AI_AGENT', 'GUARDRAIL_ENGINE', 'HUMAN'
        :param decision: e.g., 'ALLOWED', 'BLOCKED', 'SEND_PAYMENT_LINK'
        :param reason: Clear text explanation of the decision
        :param evidence: List of facts used to make the decision
        :param additional_context: Any other metadata
        """
        log_data = {
            "case_id": case_id,
            "timestamp": datetime.utcnow(),
            "stage": stage,
            "actor": actor,
            "decision": decision,
            "reason": reason,
            "evidence": evidence or [],
            "additional_context": additional_context or {}
        }
        
        return AuditRepository.add_log(log_data)
