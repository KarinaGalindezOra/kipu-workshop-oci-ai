from pathlib import Path

import pytest

from lab01_agent_memory.experiment_catalog import load_context_experiment
from lab01_agent_memory.procedure_builder import ProcedureDefinition


EXERCISES_DIR = Path(__file__).resolve().parents[1] / "exercises"


def test_context_experiment_resolves_only_declared_synthetic_procedures() -> None:
    plan = load_context_experiment(EXERCISES_DIR / "context-economy-experiment.json")

    assert plan.experiment_id == "payment-context-economy-v1"
    assert len(plan.procedures) == 5
    assert len(plan.variants) == 4
    assert plan.variants[1].variant_id == "retrieved-top-1"


def test_procedure_definition_rejects_non_synthetic_or_invalid_identifier() -> None:
    payload = {
        "synthetic": False,
        "procedure_id": "Refund Approval",
        "title": "Refund approval",
        "version": "1.0",
        "domain": "payments",
        "trigger_terms": ["refund"],
        "procedure": "Approve synthetic refund.",
        "required_evidence": ["reference"],
    }
    with pytest.raises(ValueError, match="synthetic"):
        ProcedureDefinition.from_payload(payload)

    payload["synthetic"] = True
    with pytest.raises(ValueError, match="procedure_id"):
        ProcedureDefinition.from_payload(payload)
