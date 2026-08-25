import pytest
from services.diagnosis import DiagnosisService

def test_diagnosis_insufficient_funds():
    service = DiagnosisService()
    case = {"failure_reason": "insufficient_funds", "customer_tenure_days": 100, "failed_payments": 2}
    result = service.analyze(case)
    assert any("insufficient_funds" in e for e in result["evidence"])

def test_diagnosis_network_error():
    service = DiagnosisService()
    case = {"failure_reason": "network_error", "customer_tenure_days": 10, "failed_payments": 1}
    result = service.analyze(case)
    assert any("network_error" in e for e in result["evidence"])

def test_diagnosis_suspected_fraud():
    service = DiagnosisService()
    case = {"failure_reason": "suspected_fraud", "customer_tenure_days": 5, "failed_payments": 1}
    result = service.analyze(case)
    assert any("suspected_fraud" in e for e in result["evidence"])
