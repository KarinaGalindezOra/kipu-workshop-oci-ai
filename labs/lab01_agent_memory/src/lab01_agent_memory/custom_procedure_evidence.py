"""Validate safe evidence from participant-authored procedure exercises."""

from __future__ import annotations

import json
from typing import Any


def _text(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Custom procedure evidence field '{field}' must be a non-empty string")
    return value.strip()


def _text_list(payload: dict[str, Any], field: str) -> list[str]:
    value = payload.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"Custom procedure evidence field '{field}' must be a non-empty string list")
    return [item.strip() for item in value]


def load_custom_procedure_evidence(raw_json: str) -> dict[str, object]:
    """Load bounded evidence without accepting credentials or raw memory content."""

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise ValueError("The custom procedure evidence is not valid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("The custom procedure evidence root must be a JSON object")
    if payload.get("evidence_type") != "oci_custom_procedure_validation":
        raise ValueError("The JSON is not custom procedure evidence")
    if payload.get("contains_no_secrets") is not True:
        raise ValueError("Custom procedure evidence must declare contains_no_secrets=true")
    procedure = payload.get("procedure")
    execution = payload.get("sdk_execution")
    study = payload.get("retrieval_study")
    if not isinstance(procedure, dict) or not isinstance(execution, dict) or not isinstance(study, list):
        raise ValueError("Custom procedure evidence requires procedure, sdk_execution, and retrieval_study")
    for field in ("persistence_confirmed", "targeted_retrieval_confirmed", "negative_control_passed"):
        if execution.get(field) is not True:
            raise ValueError(f"Custom procedure evidence did not approve {field}")
    if len(study) != 3:
        raise ValueError("Custom procedure evidence must contain exactly three retrieval cases")
    normalized_study: list[dict[str, object]] = []
    for case in study:
        if not isinstance(case, dict):
            raise ValueError("Custom procedure retrieval case must be an object")
        count = case.get("result_count")
        if not isinstance(count, int) or count < 0:
            raise ValueError("Custom procedure retrieval result_count must be non-negative")
        retrieved = case.get("custom_procedure_retrieved")
        if not isinstance(retrieved, bool):
            raise ValueError("Custom procedure retrieval status must be boolean")
        normalized_study.append(
            {
                "label": _text(case, "label"),
                "query": _text(case, "query"),
                "result_count": count,
                "custom_procedure_retrieved": retrieved,
            }
        )
    return {
        "active_team_id": _text(payload, "active_team_id"),
        "participant_code": _text(payload, "participant_code"),
        "procedure": {
            "procedure_id": _text(procedure, "procedure_id"),
            "title": _text(procedure, "title"),
            "version": _text(procedure, "version"),
            "domain": _text(procedure, "domain"),
            "trigger_terms": _text_list(procedure, "trigger_terms"),
            "required_evidence": _text_list(procedure, "required_evidence"),
        },
        "retrieval_study": normalized_study,
        "sdk_execution": {
            "individual_scope": _text(execution, "individual_scope"),
            "created": execution.get("created"),
            "existing": execution.get("existing"),
        },
    }
