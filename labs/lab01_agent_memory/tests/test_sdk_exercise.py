from dataclasses import dataclass
from pathlib import Path

from lab01_agent_memory.participant_lab import load_bundle
from lab01_agent_memory.sdk_exercise import (
    build_team_scopes,
    run_memory_exercise,
    run_sdk_exercise,
)


@dataclass(frozen=True)
class Record:
    content: str


class FakeAgentMemory:
    def __init__(self) -> None:
        self.records: dict[str, list[Record]] = {}

    def list_memories(self, *, user_id: str, limit: int) -> list[Record]:
        return self.records.get(user_id, [])[:limit]

    def add_memory(self, content: str, **kwargs: object) -> Record:
        record = Record(content=content)
        self.records.setdefault(str(kwargs["user_id"]), []).append(record)
        return record

    def search(
        self, query: str, *, user_id: str, record_types: list[str]
    ) -> list[Record]:
        query_terms = set(query.lower().split())
        return [
            record
            for record in self.records.get(user_id, [])
            if query_terms.intersection(record.content.lower().split())
        ]


EXERCISES_DIR = Path(__file__).resolve().parents[1] / "exercises"


def test_team_scopes_are_deterministic_and_distinct() -> None:
    scopes = build_team_scopes("T01", "P02")

    assert scopes.individual == "t01:p02"
    assert scopes.shared == "t01:shared"
    assert scopes.control == "t01:control"


def test_sdk_exercise_persists_individual_and_shared_memory_without_cross_scope_results() -> None:
    memory = FakeAgentMemory()
    bundle = load_bundle(EXERCISES_DIR / "team_payments_memory.json")

    result = run_sdk_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        publish_to_team_scope=True,
    )

    evidence = result.evidence
    assert evidence["evidence_type"] == "oci_sdk_execution_validation"
    assert evidence["isolation_passed"] is True
    assert evidence["retrieved_procedure_ids"] == ["payment-idempotency"]
    assert evidence["persisted_procedure_ids"] == [
        "payment-idempotency",
        "contract-compatibility",
    ]
    assert evidence["sdk_execution"]["individual_created"] == 2
    assert evidence["sdk_execution"]["team_shared_result_count"] == 1
    assert evidence["sdk_execution"]["persistence_confirmed"] is True


def test_sdk_exercise_is_idempotent_on_rerun() -> None:
    memory = FakeAgentMemory()
    bundle = load_bundle(EXERCISES_DIR / "team_payments_memory.json")

    run_sdk_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        publish_to_team_scope=False,
    )
    result = run_sdk_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        publish_to_team_scope=False,
    )

    assert result.evidence["sdk_execution"]["individual_created"] == 0
    assert result.evidence["sdk_execution"]["individual_existing"] == 2


def test_memory_exercise_persists_and_recovers_one_selected_procedure_without_inference() -> None:
    memory = FakeAgentMemory()
    bundle = load_bundle(EXERCISES_DIR / "team_payments_memory.json")

    result = run_memory_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        procedure_id="contract-compatibility",
    )

    evidence = result.evidence
    assert evidence["exercise_mode"] == "memory_only"
    assert evidence["selected_procedure_id"] == "contract-compatibility"
    assert evidence["retrieved_procedure_ids"] == ["contract-compatibility"]
    assert evidence["sdk_execution"]["individual_created"] == 1
    assert evidence["sdk_execution"]["persistence_confirmed"] is True
    assert evidence["isolation_passed"] is True


def test_memory_exercise_is_idempotent_for_the_selected_procedure() -> None:
    memory = FakeAgentMemory()
    bundle = load_bundle(EXERCISES_DIR / "team_payments_memory.json")

    run_memory_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        procedure_id="payment-idempotency",
    )
    result = run_memory_exercise(
        memory,
        bundle,
        team_code="T01",
        participant_code="P01",
        procedure_id="payment-idempotency",
    )

    assert result.evidence["sdk_execution"]["individual_created"] == 0
    assert result.evidence["sdk_execution"]["individual_existing"] == 1
