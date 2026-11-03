import json

import pytest
from lab01_agent_memory.custom_procedure_evidence import load_custom_procedure_evidence


def _payload() -> dict[str, object]:
    return {
        "evidence_type": "oci_custom_procedure_validation", "contains_no_secrets": True,
        "active_team_id": "T01", "participant_code": "P01",
        "procedure": {"procedure_id": "refund-traceability-v1", "title": "Refund", "version": "1.0", "domain": "payments", "trigger_terms": ["refund"], "required_evidence": ["reference"]},
        "retrieval_study": [
            {"label": "targeted", "query": "refund", "result_count": 1, "custom_procedure_retrieved": True},
            {"label": "broad", "query": "payments", "result_count": 1, "custom_procedure_retrieved": True},
            {"label": "negative_control", "query": "migration", "result_count": 0, "custom_procedure_retrieved": False},
        ],
        "sdk_execution": {"individual_scope": "t01:p01", "created": 1, "existing": 0, "persistence_confirmed": True, "targeted_retrieval_confirmed": True, "negative_control_passed": True},
    }


def test_custom_procedure_evidence_accepts_approved_study() -> None:
    assert load_custom_procedure_evidence(json.dumps(_payload()))["participant_code"] == "P01"


def test_custom_procedure_evidence_rejects_failed_control() -> None:
    payload = _payload()
    payload["sdk_execution"]["negative_control_passed"] = False
    with pytest.raises(ValueError, match="negative_control_passed"):
        load_custom_procedure_evidence(json.dumps(payload))
