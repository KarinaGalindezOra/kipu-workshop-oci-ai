import json

import pytest

from lab01_agent_memory.experiment_evidence import load_context_experiment_evidence


def _payload() -> dict[str, object]:
    return {
        "evidence_type": "oci_context_experiment_validation",
        "contains_no_secrets": True,
        "active_team_id": "T01",
        "participant_code": "P01",
        "experiment": {"experiment_id": "context-v1", "title": "Context", "question": "Question", "retrieval_query": "idempotency"},
        "memory_execution": {
            "schema_policy": "REQUIRE_EXISTING", "search_strategy": "KEYWORD",
            "persistence_confirmed": True, "isolation_passed": True,
            "individual_scope": "t01:p01", "persisted_procedure_ids": ["payment-v1"],
            "retrieved_procedure_ids": ["payment-v1"], "individual_created": 1, "individual_existing": 0,
        },
        "inference_experiment": {
            "measurement_type": "oci_context_experiment", "model_id": "approved-model", "max_output_tokens": 120,
            "all_quality_checks_passed": True, "baseline_variant_id": "baseline",
            "lowest_input_variant_id": "retrieved", "lowest_input_reduction_from_baseline": 50,
            "variants": [
                {"variant_id": "baseline", "label": "Baseline", "procedure_ids": ["payment-v1"], "procedure_count": 1, "prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "latency_ms": 100, "quality_passed": True, "finish_reason": "COMPLETE"},
                {"variant_id": "retrieved", "label": "Retrieved", "procedure_ids": ["payment-v1"], "procedure_count": 1, "prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70, "latency_ms": 90, "quality_passed": True, "finish_reason": "COMPLETE"},
            ],
        },
    }


def test_context_experiment_evidence_requires_safe_consistent_usage() -> None:
    assert load_context_experiment_evidence(json.dumps(_payload()))["participant_code"] == "P01"
    payload = _payload()
    payload["inference_experiment"]["variants"][0]["total_tokens"] = 1
    with pytest.raises(ValueError, match="inconsistent"):
        load_context_experiment_evidence(json.dumps(payload))
