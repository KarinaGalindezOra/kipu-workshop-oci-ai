"""Tests for safe, bounded context-experiment evidence."""

from __future__ import annotations

import json

import pytest
from lab01_agent_memory.experiment_evidence import load_context_experiment_evidence


def _evidence() -> dict[str, object]:
    return {
        "evidence_type": "oci_context_experiment_validation",
        "contains_no_secrets": True,
        "active_team_id": "T01",
        "participant_code": "P01",
        "experiment": {
            "experiment_id": "payment-context-economy-v1",
            "title": "Context economy",
            "question": "How do we process a repeated payment request?",
            "retrieval_query": "idempotency",
        },
        "memory_execution": {
            "schema_policy": "REQUIRE_EXISTING",
            "search_strategy": "KEYWORD",
            "persistence_confirmed": True,
            "isolation_passed": True,
            "individual_scope": "t01:p01",
            "persisted_procedure_ids": ["payment-idempotency-v1"],
            "retrieved_procedure_ids": ["payment-idempotency-v1"],
            "individual_created": 1,
            "individual_existing": 4,
        },
        "inference_experiment": {
            "measurement_type": "oci_context_experiment",
            "model_id": "cohere.command-a-03-2025",
            "max_output_tokens": 120,
            "all_quality_checks_passed": True,
            "baseline_variant_id": "all-rules-baseline",
            "lowest_input_variant_id": "retrieved-top-1",
            "lowest_input_reduction_from_baseline": 90,
            "variants": [
                {
                    "variant_id": "all-rules-baseline",
                    "label": "All rules",
                    "procedure_ids": ["payment-idempotency-v1", "audit-traceability-v1"],
                    "procedure_count": 2,
                    "prompt_tokens": 160,
                    "completion_tokens": 20,
                    "total_tokens": 180,
                    "latency_ms": 410,
                    "quality_passed": True,
                    "finish_reason": "COMPLETE",
                },
                {
                    "variant_id": "retrieved-top-1",
                    "label": "Retrieved top 1",
                    "procedure_ids": ["payment-idempotency-v1"],
                    "procedure_count": 1,
                    "prompt_tokens": 70,
                    "completion_tokens": 20,
                    "total_tokens": 90,
                    "latency_ms": 330,
                    "quality_passed": True,
                    "finish_reason": "COMPLETE",
                },
            ],
        },
    }


def test_load_context_experiment_evidence_accepts_safe_complete_measurement() -> None:
    evidence = load_context_experiment_evidence(json.dumps(_evidence()))

    assert evidence["active_team_id"] == "T01"
    assert evidence["inference_experiment"]["lowest_input_variant_id"] == "retrieved-top-1"
    assert len(evidence["inference_experiment"]["variants"]) == 2


def test_load_context_experiment_evidence_rejects_inconsistent_usage() -> None:
    payload = _evidence()
    payload["inference_experiment"]["variants"][0]["total_tokens"] = 999

    with pytest.raises(ValueError, match="inconsistent"):
        load_context_experiment_evidence(json.dumps(payload))
