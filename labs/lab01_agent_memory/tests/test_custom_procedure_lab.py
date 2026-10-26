"""Tests for participant-authored synthetic procedure persistence and retrieval."""

from dataclasses import dataclass

from lab01_agent_memory.custom_procedure_lab import run_custom_procedure_exercise
from lab01_agent_memory.procedure_builder import ProcedureDefinition


@dataclass
class Record:
    content: str


class InMemoryMemory:
    def __init__(self) -> None:
        self.records: dict[str, list[Record]] = {}

    def list_memories(self, *, user_id: str, limit: int) -> list[Record]:
        return self.records.get(user_id, [])[:limit]

    def add_memory(self, content: str, **kwargs: object) -> Record:
        record = Record(content)
        self.records.setdefault(str(kwargs["user_id"]), []).append(record)
        return record

    def search(self, query: str, *, user_id: str, record_types: list[str]) -> list[Record]:
        terms = query.casefold().split()
        return [record for record in self.records.get(user_id, []) if all(term in record.content.casefold() for term in terms)]


def test_custom_procedure_is_idempotent_and_has_targeted_retrieval() -> None:
    procedure = ProcedureDefinition.from_payload({
        "synthetic": True, "procedure_id": "refund-traceability-v1", "title": "Refund",
        "version": "1.0", "domain": "payments", "trigger_terms": ["refund", "approval"],
        "procedure": "Validate a synthetic refund approval and preserve traceability.",
        "required_evidence": ["approval reference"],
    })
    memory = InMemoryMemory()
    first = run_custom_procedure_exercise(memory, procedure, team_code="T01", participant_code="P01")
    second = run_custom_procedure_exercise(memory, procedure, team_code="T01", participant_code="P01")
    assert first.evidence["sdk_execution"]["created"] == 1
    assert second.evidence["sdk_execution"]["existing"] == 1
    assert first.evidence["sdk_execution"]["targeted_retrieval_confirmed"] is True
    assert first.evidence["sdk_execution"]["negative_control_passed"] is True
