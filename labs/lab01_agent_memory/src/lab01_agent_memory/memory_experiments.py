"""Agent Memory preparation and retrieval evidence for context experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .experiment_catalog import ContextExperimentPlan
from .sdk_exercise import AGENT_ID, AgentMemoryAdapter, TeamScopes, build_team_scopes


def _record_content(record: Any) -> str:
    content = getattr(record, "content", None)
    if not isinstance(content, str):
        raise ValueError("Agent Memory returned a record without string content")
    return content


def _exists(memory: AgentMemoryAdapter, scope: str, content: str) -> bool:
    return any(
        _record_content(record) == content
        for record in memory.list_memories(user_id=scope, limit=100)
    )


@dataclass(frozen=True)
class ContextExperimentMemoryResult:
    """Safe facts proving real persistence, retrieval, and scope isolation."""

    scopes: TeamScopes
    created: int
    existing: int
    persisted_procedure_ids: tuple[str, ...]
    retrieved_procedure_ids: tuple[str, ...]
    isolation_passed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_policy": "REQUIRE_EXISTING",
            "search_strategy": "KEYWORD",
            "individual_scope": self.scopes.individual,
            "team_shared_scope": self.scopes.shared,
            "control_scope": self.scopes.control,
            "individual_created": self.created,
            "individual_existing": self.existing,
            "persisted_procedure_ids": list(self.persisted_procedure_ids),
            "retrieved_procedure_ids": list(self.retrieved_procedure_ids),
            "persistence_confirmed": True,
            "isolation_passed": self.isolation_passed,
        }


def prepare_context_experiment_memory(
    memory: AgentMemoryAdapter,
    plan: ContextExperimentPlan,
    *,
    team_code: str,
    participant_code: str,
) -> ContextExperimentMemoryResult:
    """Persist a catalog in one scope and retrieve the lead rule through Agent Memory.

    The catalog is idempotent. The selected retrieval is based on an actual SDK
    keyword search; deliberately noisy variants are assembled later only for
    the inference experiment so their effect remains explicit and measurable.
    """

    scopes = build_team_scopes(team_code, participant_code)
    created = 0
    existing = 0
    contents = plan.procedure_contents()
    for procedure in plan.procedures:
        content = contents[procedure.procedure_id]
        if _exists(memory, scopes.individual, content):
            existing += 1
            continue
        metadata = procedure.as_metadata() | {
            "team_code": team_code,
            "participant_code": participant_code,
            "experiment_id": plan.experiment_id,
        }
        memory.add_memory(
            content,
            memory_type="guideline",
            user_id=scopes.individual,
            agent_id=AGENT_ID,
            metadata=metadata,
        )
        created += 1

    persisted_content = {
        _record_content(record)
        for record in memory.list_memories(user_id=scopes.individual, limit=100)
    }
    persisted_ids = tuple(
        procedure.procedure_id
        for procedure in plan.procedures
        if contents[procedure.procedure_id] in persisted_content
    )
    if len(persisted_ids) != len(plan.procedures):
        raise RuntimeError("Not all context experiment procedures were persisted")

    retrieved_content = [
        _record_content(record)
        for record in memory.search(
            plan.retrieval_query,
            user_id=scopes.individual,
            record_types=["guideline"],
        )
    ]
    retrieved_ids = tuple(
        procedure.procedure_id
        for procedure in plan.procedures
        if contents[procedure.procedure_id] in retrieved_content
    )
    if not retrieved_ids:
        raise RuntimeError("The experiment retrieval query did not return a catalog procedure")
    control_results = list(
        memory.search(
            plan.control_query,
            user_id=scopes.individual,
            record_types=["guideline"],
        )
    )
    return ContextExperimentMemoryResult(
        scopes=scopes,
        created=created,
        existing=existing,
        persisted_procedure_ids=persisted_ids,
        retrieved_procedure_ids=retrieved_ids,
        isolation_passed=not control_results,
    )
