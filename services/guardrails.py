import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GuardrailEngine:
    def __init__(self):
        pass

    @property
    def max_recovery_attempts(self):
        try:
            import streamlit as st
            if 'max_recovery_attempts' in st.session_state:
                return int(st.session_state.max_recovery_attempts)
        except ImportError:
            pass
        return int(os.getenv("MAX_RECOVERY_ATTEMPTS", "2"))

    @property
    def max_contact_attempts(self):
        try:
            import streamlit as st
            if 'max_contact_attempts' in st.session_state:
                return int(st.session_state.max_contact_attempts)
        except ImportError:
            pass
        return int(os.getenv("MAX_CONTACT_ATTEMPTS", "3"))

    @property
    def min_ai_confidence(self):
        try:
            import streamlit as st
            if 'min_ai_confidence' in st.session_state:
                return float(st.session_state.min_ai_confidence)
        except ImportError:
            pass
        return float(os.getenv("MIN_AI_CONFIDENCE", "0.60"))

    @property
    def high_value_threshold(self):
        try:
            import streamlit as st
            if 'high_value_threshold' in st.session_state:
                return float(st.session_state.high_value_threshold)
        except ImportError:
            pass
        return float(os.getenv("HIGH_VALUE_THRESHOLD", "10000"))
        
    def validate_action(
        self, 
        case_data: Dict[str, Any], 
        ai_recommendation: Dict[str, Any], 
        expected_recovery_value: float
    ) -> Dict[str, Any]:
        """
        Validates the AI's recommended action against strict deterministic rules.
        """
        action = ai_recommendation.get('action')
        confidence = ai_recommendation.get('confidence', 0.0)
        
        amount = case_data.get('transaction_amount', 0.0)
        already_paid = case_data.get('already_paid', False)
        recovery_attempts = case_data.get('previous_recovery_attempts', 0)
        contact_attempts = case_data.get('contact_attempts', 0)
        previous_action = case_data.get('previous_action', None)
        
        rules_triggered = []
        
        # Rule 1: Already paid
        if already_paid:
            return {
                "decision": "STOP",
                "reason": "Payment already recovered",
                "rules_triggered": ["already_paid"],
                "execution_permitted": False
            }
            
        # Rule 2: Max recovery attempts
        if recovery_attempts >= self.max_recovery_attempts:
            return {
                "decision": "BLOCK",
                "reason": "Maximum recovery attempts reached",
                "rules_triggered": ["max_recovery_attempts"],
                "execution_permitted": False
            }
            
        # Rule 3: Max contact attempts
        if contact_attempts >= self.max_contact_attempts:
            return {
                "decision": "BLOCK",
                "reason": "Maximum contact attempts reached",
                "rules_triggered": ["max_contact_attempts"],
                "execution_permitted": False
            }
            
        # Rule 4: Duplicate action
        if action == previous_action and action != "WAIT":
            return {
                "decision": "BLOCK",
                "reason": f"Cannot execute duplicate action: {action}",
                "rules_triggered": ["duplicate_action"],
                "execution_permitted": False
            }
            
        # Rule 5: Low AI confidence
        if confidence < self.min_ai_confidence and action != "STOP":
            return {
                "decision": "ESCALATE",
                "reason": "AI confidence is too low",
                "rules_triggered": ["low_ai_confidence"],
                "execution_permitted": False
            }
            
        # Rule 6: High value threshold
        if amount > self.high_value_threshold and action != "STOP":
            return {
                "decision": "REQUIRE_APPROVAL",
                "reason": "Transaction amount exceeds automatic execution threshold",
                "rules_triggered": ["high_value_threshold"],
                "execution_permitted": False
            }
            
        # Rule 7: Low expected recovery value
        # Define a minimum intervention cost equivalent
        min_intervention_cost = float(os.getenv("INTERVENTION_COST", "50.0")) 
        if expected_recovery_value < min_intervention_cost and action != "STOP":
            return {
                "decision": "STOP",
                "reason": "Expected recovery value is too low to justify intervention",
                "rules_triggered": ["low_expected_value"],
                "execution_permitted": False
            }
            
        # If all checks pass
        return {
            "decision": "ALLOW",
            "reason": "All safety checks passed",
            "rules_triggered": [],
            "execution_permitted": True
        }
