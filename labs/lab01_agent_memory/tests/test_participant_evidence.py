import json

import pytest
from lab01_agent_memory.participant_evidence import load_participant_evidence


def _approved_evidence() -> dict[str, object]:
    return {
        "active_team_id": "team-payments",
        "active_team_name": "Payments API",
        "algorithm": {
            "scope": "team-payments",
            "query": "payment idempotency contract v2",
            "max_results": 2,
        },
        "retrieved_procedure_ids": ["payment-idempotency", "contract-compatibility"],
        "cross_team_challenge": "database migration controlled phases",
        "cross_team_visible_procedure_ids": [],
        "isolation_passed": True,
        "prompt_comparison": {
            "baseline_prompt_tokens": 99,
            "memory_prompt_tokens": 14,
            "retrieved_guideline_tokens": 43,
            "estimated_request_tokens_with_memory": 57,
            "repeated_prompt_reduction_tokens": 85,
            "estimated_request_reduction_tokens": 42,
        },
        "evidence_type": "local_algorithm_validation",
        "contains_no_secrets": True,
    }


def test_load_participant_evidence_accepts_the_approved_algorithm_output() -> None:
    evidence = load_participant_evidence(json.dumps(_approved_evidence()))

    assert evidence["active_team_id"] == "team-payments"
    assert evidence["retrieved_procedure_ids"] == [
        "payment-idempotency",
        "contract-compatibility",
    ]
    assert evidence["cross_team_visible_procedure_ids"] == []


def test_load_participant_evidence_rejects_cross_team_content() -> None:
    evidence = _approved_evidence()
    evidence["cross_team_visible_procedure_ids"] = ["migration-rollout"]

    with pytest.raises(ValueError, match="cross-team"):
        load_participant_evidence(json.dumps(evidence))


def test_load_participant_evidence_accepts_memory_only_sdk_evidence() -> None:
    evidence = _approved_evidence()
    evidence["evidence_type"] = "oci_sdk_execution_validation"
    evidence["exercise_mode"] = "memory_only"
    evidence["selected_procedure_id"] = "payment-idempotency"
    evidence["algorithm"]["record_types"] = ["guideline"]
    evidence["persisted_procedure_ids"] = ["payment-idempotency"]
    evidence["sdk_execution"] = {
        "schema_policy": "REQUIRE_EXISTING",
        "search_strategy": "KEYWORD",
        "individual_scope": "t01:p01",
        "team_shared_scope": "t01:shared",
        "control_scope": "t01:control",
        "individual_created": 1,
        "individual_existing": 0,
        "team_shared_created": 0,
        "team_shared_existing": 0,
        "team_shared_result_count": 0,
        "persistence_confirmed": True,
    }

    loaded = load_participant_evidence(json.dumps(evidence))

    assert loaded["exercise_mode"] == "memory_only"
    assert loaded["selected_procedure_id"] == "payment-idempotency"


def test_load_participant_evidence_accepts_real_sdk_evidence() -> None:
    evidence = _approved_evidence()
    evidence["evidence_type"] = "oci_sdk_execution_validation"
    evidence["algorithm"]["record_types"] = ["guideline"]
    evidence["persisted_procedure_ids"] = [
        "payment-idempotency",
        "contract-compatibility",
    ]
    evidence["sdk_execution"] = {
        "schema_policy": "REQUIRE_EXISTING",
        "search_strategy": "KEYWORD",
        "individual_scope": "t01:p01",
        "team_shared_scope": "t01:shared",
        "control_scope": "t01:control",
        "individual_created": 2,
        "individual_existing": 0,
        "team_shared_created": 2,
        "team_shared_existing": 0,
        "team_shared_result_count": 2,
        "persistence_confirmed": True,
    }

    loaded = load_participant_evidence(json.dumps(evidence))

    assert loaded["evidence_type"] == "oci_sdk_execution_validation"
    assert loaded["sdk_execution"]["individual_scope"] == "t01:p01"
    assert loaded["algorithm"]["record_types"] == ["guideline"]
    assert loaded["persisted_procedure_ids"] == [
        "payment-idempotency",
        "contract-compatibility",
    ]


def test_load_participant_evidence_rejects_sdk_creation_policy() -> None:
    evidence = _approved_evidence()
    evidence["evidence_type"] = "oci_sdk_execution_validation"
    evidence["algorithm"]["record_types"] = ["guideline"]
    evidence["persisted_procedure_ids"] = [
        "payment-idempotency",
        "contract-compatibility",
    ]
    evidence["sdk_execution"] = {
        "schema_policy": "CREATE_IF_EMPTY",
        "search_strategy": "KEYWORD",
        "individual_scope": "t01:p01",
        "team_shared_scope": "t01:shared",
        "control_scope": "t01:control",
        "individual_created": 2,
        "individual_existing": 0,
        "team_shared_created": 0,
        "team_shared_existing": 0,
        "team_shared_result_count": 0,
        "persistence_confirmed": True,
    }

    with pytest.raises(ValueError, match="REQUIRE_EXISTING"):
        load_participant_evidence(json.dumps(evidence))


def test_load_participant_evidence_accepts_real_oci_inference_usage() -> None:
    evidence = _approved_evidence()
    evidence["evidence_type"] = "oci_sdk_inference_validation"
    evidence["algorithm"]["record_types"] = ["guideline"]
    evidence["persisted_procedure_ids"] = ["payment-idempotency", "contract-compatibility"]
    evidence["sdk_execution"] = {
        "schema_policy": "REQUIRE_EXISTING",
        "search_strategy": "KEYWORD",
        "individual_scope": "t01:p01",
        "team_shared_scope": "t01:shared",
        "control_scope": "t01:control",
        "individual_created": 2,
        "individual_existing": 0,
        "team_shared_created": 0,
        "team_shared_existing": 0,
        "team_shared_result_count": 0,
        "persistence_confirmed": True,
    }
    evidence["inference"] = {
        "measurement_type": "oci_inference_usage",
        "model_id": "approved-chat-model",
        "max_output_tokens": 120,
        "baseline": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "latency_ms": 380,
            "quality_passed": True,
            "finish_reason": "COMPLETE",
        },
        "memory_optimized": {
            "prompt_tokens": 55,
            "completion_tokens": 20,
            "total_tokens": 75,
            "latency_ms": 310,
            "quality_passed": True,
            "finish_reason": "COMPLETE",
        },
        "input_token_reduction": 45,
        "input_token_reduction_percent": 45,
        "both_quality_checks_passed": True,
    }

    loaded = load_participant_evidence(json.dumps(evidence))

    assert loaded["inference"]["input_token_reduction"] == 45
    assert loaded["inference"]["memory_optimized"]["prompt_tokens"] == 55


def test_load_participant_evidence_rejects_non_reduced_provider_usage() -> None:
    evidence = _approved_evidence()
    evidence["evidence_type"] = "oci_sdk_inference_validation"
    evidence["algorithm"]["record_types"] = ["guideline"]
    evidence["persisted_procedure_ids"] = ["payment-idempotency"]
    evidence["sdk_execution"] = {
        "schema_policy": "REQUIRE_EXISTING",
        "search_strategy": "KEYWORD",
        "individual_scope": "t01:p01",
        "team_shared_scope": "t01:shared",
        "control_scope": "t01:control",
        "individual_created": 1,
        "individual_existing": 0,
        "team_shared_created": 0,
        "team_shared_existing": 0,
        "team_shared_result_count": 0,
        "persistence_confirmed": True,
    }
    evidence["inference"] = {
        "measurement_type": "oci_inference_usage",
        "model_id": "approved-chat-model",
        "max_output_tokens": 120,
        "baseline": {
            "prompt_tokens": 55,
            "completion_tokens": 20,
            "total_tokens": 75,
            "latency_ms": 1,
            "quality_passed": True,
            "finish_reason": "COMPLETE",
        },
        "memory_optimized": {
            "prompt_tokens": 55,
            "completion_tokens": 20,
            "total_tokens": 75,
            "latency_ms": 1,
            "quality_passed": True,
            "finish_reason": "COMPLETE",
        },
        "input_token_reduction": 0,
        "input_token_reduction_percent": 0,
        "both_quality_checks_passed": True,
    }

    with pytest.raises(ValueError, match="did not reduce"):
        load_participant_evidence(json.dumps(evidence))
