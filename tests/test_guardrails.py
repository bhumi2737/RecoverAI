import os
import pytest
from services.guardrails import GuardrailEngine

@pytest.fixture
def guardrail_engine():
    # Set default values for tests if not set in env
    os.environ['MAX_RECOVERY_ATTEMPTS'] = '2'
    os.environ['MAX_CONTACT_ATTEMPTS'] = '3'
    os.environ['MIN_AI_CONFIDENCE'] = '0.60'
    os.environ['HIGH_VALUE_THRESHOLD'] = '10000'
    os.environ['INTERVENTION_COST'] = '50.0'
    return GuardrailEngine()

def test_guardrails_already_paid(guardrail_engine):
    case_info = {"already_paid": True}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "STOP"

def test_guardrails_max_recovery_attempts(guardrail_engine):
    case_info = {"previous_recovery_attempts": 3, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "BLOCK"

def test_guardrails_max_contact_attempts(guardrail_engine):
    case_info = {"contact_attempts": 4, "previous_recovery_attempts": 1, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "BLOCK"

def test_guardrails_duplicate_action(guardrail_engine):
    case_info = {"previous_action": "SEND_PAYMENT_LINK", "contact_attempts": 1, "previous_recovery_attempts": 1, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "BLOCK"

def test_guardrails_low_confidence(guardrail_engine):
    case_info = {"contact_attempts": 1, "previous_recovery_attempts": 1, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.5}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "ESCALATE"

def test_guardrails_high_value(guardrail_engine):
    case_info = {"transaction_amount": 15000, "contact_attempts": 1, "previous_recovery_attempts": 1, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 10000)
    assert res["decision"] == "REQUIRE_APPROVAL"

def test_guardrails_valid_safe_action(guardrail_engine):
    case_info = {"transaction_amount": 1500, "contact_attempts": 1, "previous_recovery_attempts": 1, "already_paid": False}
    ai_rec = {"action": "SEND_PAYMENT_LINK", "confidence": 0.9}
    res = guardrail_engine.validate_action(case_info, ai_rec, 1000)
    assert res["decision"] == "ALLOW"
