"""Validate safe evidence emitted by extended real OCI context experiments."""

from __future__ import annotations

import json
from typing import Any


def _string(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Experiment evidence field '{field}' must be a non-empty string")
    return value.strip()


def _non_negative_int(payload: dict[str, Any], field: str) -> int:
    value = payload.get(field)
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"Experiment evidence field '{field}' must be a non-negative integer")
    return value


def _string_list(payload: dict[str, Any], field: str) -> list[str]:
    value = payload.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"Experiment evidence field '{field}' must be an array of non-empty strings")
    return [item.strip() for item in value]


def load_context_experiment_evidence(raw_json: str) -> dict[str, object]:
    """Load only a bounded, credential-free real OCI context experiment artifact."""

    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise ValueError("The context experiment evidence is not valid JSON") from error
    if not isinstance(payload, dict):
        raise ValueError("The context experiment evidence root must be a JSON object")
    if payload.get("evidence_type") != "oci_context_experiment_validation":
        raise ValueError("The JSON is not approved context experiment evidence")
    if payload.get("contains_no_secrets") is not True:
        raise ValueError("Context experiment evidence must declare contains_no_secrets=true")

    experiment = payload.get("experiment")
    memory = payload.get("memory_execution")
    inference = payload.get("inference_experiment")
    if not isinstance(experiment, dict) or not isinstance(memory, dict) or not isinstance(inference, dict):
        raise ValueError("Context experiment evidence requires experiment, memory_execution, and inference_experiment")
    if memory.get("schema_policy") != "REQUIRE_EXISTING":
        raise ValueError("Context experiment evidence must use SchemaPolicy.REQUIRE_EXISTING")
    if memory.get("search_strategy") != "KEYWORD":
        raise ValueError("Context experiment evidence must use keyword search")
    if memory.get("persistence_confirmed") is not True or memory.get("isolation_passed") is not True:
        raise ValueError("Context experiment must confirm persistence and isolation")
    if inference.get("measurement_type") != "oci_context_experiment":
        raise ValueError("Context experiment evidence must contain OCI provider usage")
    if inference.get("all_quality_checks_passed") is not True:
        raise ValueError("Context experiment must pass all quality checks")

    raw_variants = inference.get("variants")
    if not isinstance(raw_variants, list) or not 2 <= len(raw_variants) <= 8:
        raise ValueError("Context experiment must contain between 2 and 8 variants")
    variants: list[dict[str, object]] = []
    for variant in raw_variants:
        if not isinstance(variant, dict):
            raise ValueError("Context experiment variant must be an object")
        prompt = _non_negative_int(variant, "prompt_tokens")
        completion = _non_negative_int(variant, "completion_tokens")
        total = _non_negative_int(variant, "total_tokens")
        if total != prompt + completion:
            raise ValueError("Context experiment variant token usage is inconsistent")
        if variant.get("quality_passed") is not True or variant.get("finish_reason") != "COMPLETE":
            raise ValueError("Context experiment variant did not complete with approved quality")
        variants.append(
            {
                "variant_id": _string(variant, "variant_id"),
                "label": _string(variant, "label"),
                "procedure_ids": _string_list(variant, "procedure_ids"),
                "procedure_count": _non_negative_int(variant, "procedure_count"),
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "total_tokens": total,
                "latency_ms": _non_negative_int(variant, "latency_ms"),
            }
        )
    baseline_id = _string(inference, "baseline_variant_id")
    lowest_id = _string(inference, "lowest_input_variant_id")
    ids = {variant["variant_id"] for variant in variants}
    if baseline_id not in ids or lowest_id not in ids:
        raise ValueError("Context experiment references an unknown variant")

    return {
        "active_team_id": _string(payload, "active_team_id"),
        "participant_code": _string(payload, "participant_code"),
        "experiment": {
            "experiment_id": _string(experiment, "experiment_id"),
            "title": _string(experiment, "title"),
            "question": _string(experiment, "question"),
            "retrieval_query": _string(experiment, "retrieval_query"),
        },
        "memory_execution": {
            "individual_scope": _string(memory, "individual_scope"),
            "persisted_procedure_ids": _string_list(memory, "persisted_procedure_ids"),
            "retrieved_procedure_ids": _string_list(memory, "retrieved_procedure_ids"),
            "individual_created": _non_negative_int(memory, "individual_created"),
            "individual_existing": _non_negative_int(memory, "individual_existing"),
        },
        "inference_experiment": {
            "model_id": _string(inference, "model_id"),
            "max_output_tokens": _non_negative_int(inference, "max_output_tokens"),
            "variants": variants,
            "baseline_variant_id": baseline_id,
            "lowest_input_variant_id": lowest_id,
            "lowest_input_reduction_from_baseline": _non_negative_int(
                inference, "lowest_input_reduction_from_baseline"
            ),
        },
    }
