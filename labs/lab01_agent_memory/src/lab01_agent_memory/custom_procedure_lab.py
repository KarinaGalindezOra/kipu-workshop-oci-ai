"""Participant-authored synthetic procedure exercise backed by Agent Memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .procedure_builder import ProcedureDefinition
from .sdk_exercise import AGENT_ID, AgentMemoryAdapter, build_team_scopes


def _content(record: Any) -> str:
    value = getattr(record, "content", None)
    if not isinstance(value, str):
        raise ValueError("Agent Memory returned a record without string content")
    return value


@dataclass(frozen=True)
class CustomProcedureResult:
    """Safe evidence generated after a participant validates their own procedure design."""

    evidence: dict[str, object]


def run_custom_procedure_exercise(
    memory: AgentMemoryAdapter,
    procedure: ProcedureDefinition,
    *,
    team_code: str,
    participant_code: str,
) -> CustomProcedureResult:
    """Persist, retrieve, and assess one participant-authored synthetic procedure.

    No inference client is created. The three retrieval cases are intentionally
    simple and visible: targeted trigger terms, a broader single trigger term, and a
    known unrelated control phrase. They teach retrieval design without
    claiming that keyword overlap is a production-grade relevance evaluation.
    """

    scopes = build_team_scopes(team_code, participant_code)
    procedure_content = procedure.as_memory_content()
    durable_records = list(memory.list_memories(user_id=scopes.individual, limit=100))
    existing = any(_content(record) == procedure_content for record in durable_records)
    if not existing:
        memory.add_memory(
            procedure_content,
            memory_type="guideline",
            user_id=scopes.individual,
            agent_id=AGENT_ID,
            metadata=procedure.as_metadata()
            | {
                "team_code": team_code,
                "participant_code": participant_code,
                "exercise_mode": "custom_procedure",
            },
        )

    target_query = " ".join(procedure.trigger_terms[:2])
    cases = (
        ("targeted", target_query),
        ("broad", procedure.trigger_terms[0]),
        ("negative_control", "database migration controlled phases"),
    )
    study: list[dict[str, object]] = []
    for label, query in cases:
        results = list(memory.search(query, user_id=scopes.individual, record_types=["guideline"]))
        contents = [_content(record) for record in results]
        study.append(
            {
                "label": label,
                "query": query,
                "result_count": len(results),
                "custom_procedure_retrieved": procedure_content in contents,
            }
        )

    persisted_contents = {_content(record) for record in memory.list_memories(user_id=scopes.individual, limit=100)}
    persistence_confirmed = procedure_content in persisted_contents
    retrieval_confirmed = study[0]["custom_procedure_retrieved"] is True
    isolation_passed = study[2]["custom_procedure_retrieved"] is False
    if not persistence_confirmed or not retrieval_confirmed or not isolation_passed:
        raise RuntimeError("Custom procedure validation did not satisfy persistence, retrieval, and isolation")

    return CustomProcedureResult(
        evidence={
            "evidence_type": "oci_custom_procedure_validation",
            "contains_no_secrets": True,
            "active_team_id": team_code,
            "participant_code": participant_code,
            "procedure": {
                "procedure_id": procedure.procedure_id,
                "title": procedure.title,
                "version": procedure.version,
                "domain": procedure.domain,
                "trigger_terms": list(procedure.trigger_terms),
                "required_evidence": list(procedure.required_evidence),
            },
            "retrieval_study": study,
            "sdk_execution": {
                "schema_policy": "REQUIRE_EXISTING",
                "search_strategy": "KEYWORD",
                "individual_scope": scopes.individual,
                "created": 0 if existing else 1,
                "existing": 1 if existing else 0,
                "persistence_confirmed": persistence_confirmed,
                "targeted_retrieval_confirmed": retrieval_confirmed,
                "negative_control_passed": isolation_passed,
            },
        }
    )
