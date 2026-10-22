from pathlib import Path

from lab01_agent_memory.participant_lab import (
    build_participant_report,
    load_bundle,
    retrieve_team_memory,
)
from lab01_agent_memory.store import ScopedMemoryStore

EXERCISES_DIR = Path(__file__).resolve().parents[1] / "exercises"


def test_bundle_driven_algorithm_retrieves_own_team_procedures_only() -> None:
    payments = load_bundle(EXERCISES_DIR / "team_payments_memory.json")
    integrations = load_bundle(EXERCISES_DIR / "team_integrations_memory.json")

    report = build_participant_report(payments, integrations)

    assert report["retrieved_procedure_ids"] == ["payment-idempotency"]
    assert report["cross_team_visible_procedure_ids"] == []
    assert report["isolation_passed"] is True
    assert report["prompt_comparison"]["estimated_request_reduction_tokens"] > 0


def test_retrieval_requires_the_callers_team_scope() -> None:
    payments = load_bundle(EXERCISES_DIR / "team_payments_memory.json")
    store = ScopedMemoryStore()

    assert retrieve_team_memory(store, payments.team_id, payments.primary_query) == []
