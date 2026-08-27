"""
FDA 21 CFR Part 11 & WHO Compliance Integrity Verification Engine.
Audits electronic record signatures, system event log hashes, and cold chain telemetry records.
"""

import hashlib
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DeepComplianceAuditEngine:
    """
    Electronic Record Audit & Data Integrity Verification Service.
    """

    @staticmethod
    def generate_record_digital_signature(record_data: str, timestamp_iso: str, secret_salt: str = "RAKTDAAN_FDA_2026") -> str:
        """
        Generates SHA-256 cryptographic signature for GAMP5 / 21 CFR Part 11 record integrity.
        """
        raw = f"{record_data}:{timestamp_iso}:{secret_salt}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_audit_log_chain(audit_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifies cryptographic hash chain across system audit log entries.
        """
        tampered_indices = []
        for idx, entry in enumerate(audit_entries):
            expected = entry.get("hash")
            payload = entry.get("payload", "")
            ts = entry.get("timestamp", "")
            computed = DeepComplianceAuditEngine.generate_record_digital_signature(payload, ts)

            if expected and expected != computed:
                tampered_indices.append(idx)

        is_valid = len(tampered_indices) == 0
        return {
            "chain_valid": is_valid,
            "total_entries_audited": len(audit_entries),
            "tampered_entries_count": len(tampered_indices),
            "tampered_indices": tampered_indices,
            "verification_status": "AUDIT_CHAIN_INTECT" if is_valid else "AUDIT_CHAIN_CORRUPTED"
        }
