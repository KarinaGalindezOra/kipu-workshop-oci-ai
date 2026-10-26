"""Validate safe evidence emitted by the custom-procedure exercise."""

from __future__ import annotations

import json
from typing import Any


def load_custom_procedure_evidence(raw_json: str) -> dict[str, Any]:
    """Load approved custom-procedure evidence without accepting arbitrary JSON."""

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise ValueError("The custom procedure evidence is not valid JSON") from error
    if not isinstance(payload, dict) or payload.get("evidence_type") != "oci_custom_procedure_validation":
        raise ValueError("This is not custom procedure evidence")
    if payload.get("contains_no_secrets") is not True:
        raise ValueError("Custom procedure evidence must declare contains_no_secrets=true")
    procedure = payload.get("procedure")
    study = payload.get("retrieval_study")
    execution = payload.get("sdk_execution")
    if not isinstance(procedure, dict) or not isinstance(study, list) or not isinstance(execution, dict):
        raise ValueError("Custom procedure evidence has an invalid structure")
    if len(study) != 3 or {case.get("label") for case in study if isinstance(case, dict)} != {"targeted", "broad", "negative_control"}:
        raise ValueError("Custom procedure evidence must contain the three retrieval cases")
    for key in ("persistence_confirmed", "targeted_retrieval_confirmed", "negative_control_passed"):
        if execution.get(key) is not True:
            raise ValueError(f"Custom procedure evidence requires {key}=true")
    return payload
