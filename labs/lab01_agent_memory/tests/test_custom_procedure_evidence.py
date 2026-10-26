import json

import pytest

from lab01_agent_memory.custom_procedure_evidence import load_custom_procedure_evidence


def _payload() -> dict[str, object]:
    return {
        "evidence_type": "oci_custom_procedure_validation", "contains_no_secrets": True,
        "procedure": {"procedure_id": "refund-traceability-v1"},
        "retrieval_study": [
            {"label": "targeted"}, {"label": "broad"}, {"label": "negative_control"},
        ],
        "sdk_execution": {
            "persistence_confirmed": True, "targeted_retrieval_confirmed": True,
            "negative_control_passed": True,
        },
    }


def test_custom_procedure_evidence_accepts_approved_study() -> None:
    assert load_custom_procedure_evidence(json.dumps(_payload()))["evidence_type"] == "oci_custom_procedure_validation"


def test_custom_procedure_evidence_rejects_failed_control() -> None:
    payload = _payload()
    payload["sdk_execution"]["negative_control_passed"] = False
    with pytest.raises(ValueError, match="negative_control_passed"):
        load_custom_procedure_evidence(json.dumps(payload))
