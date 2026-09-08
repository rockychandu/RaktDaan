"""
Automated Unit Tests for FDA 21 CFR Part 11 Compliance & Audit Log Verification.
"""

from app.services.compliance.deep_compliance_engine import DeepComplianceAuditEngine


def test_digital_signature_generation():
    sig1 = DeepComplianceAuditEngine.generate_record_digital_signature("PAYLOAD_001", "2026-08-27T08:00:00Z")
    sig2 = DeepComplianceAuditEngine.generate_record_digital_signature("PAYLOAD_001", "2026-08-27T08:00:00Z")
    assert len(sig1) == 64
    assert sig1 == sig2


def test_audit_chain_verification_valid():
    ts = "2026-08-27T08:00:00Z"
    payload = "DONOR_CHECKUP_PASSED"
    sig = DeepComplianceAuditEngine.generate_record_digital_signature(payload, ts)

    entries = [{
        "payload": payload,
        "timestamp": ts,
        "hash": sig
    }]

    res = DeepComplianceAuditEngine.verify_audit_log_chain(entries)
    assert res["chain_valid"] is True
    assert res["tampered_entries_count"] == 0
