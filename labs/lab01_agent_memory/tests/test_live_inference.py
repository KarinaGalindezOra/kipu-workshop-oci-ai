"""Opt-in validation of provider-reported token usage for Lab 1.

This test makes two paid on-demand inference calls only when explicitly enabled.
"""

from __future__ import annotations

import os
from pathlib import Path

import oci
import pytest
from lab01_agent_memory.inference import (
    InferenceSettings,
    OciCohereInferenceClient,
    run_token_comparison,
)
from lab01_agent_memory.participant_lab import load_bundle

if os.getenv("RUN_OCI_INTEGRATION_TESTS") != "true":
    pytest.skip(
        "Set RUN_OCI_INTEGRATION_TESTS=true to make paid OCI Inference calls.",
        allow_module_level=True,
    )


def _required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.fail(f"Missing required integration setting: {name}")
    return value


def test_oci_inference_returns_comparable_provider_usage() -> None:
    """Verify the approved model returns complete usage for both synthetic prompts."""

    config = oci.config.from_file(profile_name=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT"))
    native_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config)
    client = OciCohereInferenceClient(native_client)
    settings = InferenceSettings(
        compartment_id=_required_environment("OCI_COMPARTMENT_ID"),
        model_id=_required_environment("LAB01_CHAT_MODEL_ID"),
        max_output_tokens=int(os.getenv("LAB01_MAX_OUTPUT_TOKENS", "120")),
    )
    bundle = load_bundle(
        Path(__file__).resolve().parents[1] / "exercises" / "team_payments_memory.json"
    )
    comparison = run_token_comparison(
        client,
        settings,
        question=bundle.primary_query,
        baseline_decisions=[(item.identifier, item.content) for item in bundle.procedures],
        retrieved_decisions=[(bundle.procedures[0].identifier, bundle.procedures[0].content)],
        required_terms=bundle.required_response_terms,
    )

    assert comparison["input_token_reduction"] > 0
    assert comparison["both_quality_checks_passed"] is True
