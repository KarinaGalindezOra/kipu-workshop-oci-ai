"""Core behavior for the real Oracle AI Agent Memory participant exercise.

This module deliberately has no database credentials or OCI side effects. The
command-line runner supplies an adapter backed by ``OracleAgentMemory``; tests
use an in-memory adapter to verify the workshop behavior deterministically.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from .metrics import compare_prompt_usage
from .participant_lab import MemoryBundle

_CODE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{1,15}$")
AGENT_ID = "khipu-workshop-agent"


@dataclass(frozen=True)
class TeamScopes:
    """Contain the individual, shared, and control scopes of one workshop team."""

    individual: str
    shared: str
    control: str


@dataclass(frozen=True)
class SdkExerciseResult:
    """Represent credential-free evidence produced by the SDK participant path."""

    evidence: dict[str, object]


class AgentMemoryAdapter(Protocol):
    """Define the small Agent Memory surface used by the hands-on exercise."""

    def list_memories(self, *, user_id: str, limit: int) -> Sequence[Any]:
        """Return durable memories for one exact user scope."""

    def add_memory(
        self,
        content: str,
        *,
        memory_type: str,
        user_id: str,
        agent_id: str,
        metadata: dict[str, str],
    ) -> Any:
        """Persist one synthetic procedural memory."""

    def search(
        self, query: str, *, user_id: str, record_types: list[str]
    ) -> Sequence[Any]:
        """Search memory through one user scope and logical record type."""


def _normalise_code(value: str, label: str) -> str:
    """Validate a stable, non-secret code used to derive a memory scope."""

    candidate = value.strip()
    if not _CODE_PATTERN.fullmatch(candidate):
        raise ValueError(
            f"{label} must start with a letter and use only letters, digits, underscores, "
            "or hyphens"
        )
    return candidate.lower()


def build_team_scopes(team_code: str, participant_code: str) -> TeamScopes:
    """Create deterministic scope IDs without accepting arbitrary user input at runtime."""

    team = _normalise_code(team_code, "team_code")
    participant = _normalise_code(participant_code, "participant_code")
    return TeamScopes(
        individual=f"{team}:{participant}",
        shared=f"{team}:shared",
        control=f"{team}:control",
    )


def _record_content(record: Any) -> str:
    """Read memory content from an SDK result or a test double."""

    content = getattr(record, "content", None)
    if not isinstance(content, str):
        raise ValueError("Agent Memory returned a record without string content")
    return content


def _memory_exists(memory: AgentMemoryAdapter, scope: str, content: str) -> bool:
    """Make exercise writes idempotent when a participant reruns the command."""

    records = memory.list_memories(user_id=scope, limit=100)
    return any(_record_content(record) == content for record in records)


def _add_bundle(
    memory: AgentMemoryAdapter,
    bundle: MemoryBundle,
    *,
    scope: str,
    team_code: str,
    participant_code: str,
) -> tuple[int, int]:
    """Persist missing procedures and report created versus existing records."""

    created = 0
    existing = 0
    for procedure in bundle.procedures:
        if _memory_exists(memory, scope, procedure.content):
            existing += 1
            continue
        memory.add_memory(
            procedure.content,
            memory_type="guideline",
            user_id=scope,
            agent_id=AGENT_ID,
            metadata={
                "team_code": team_code,
                "participant_code": participant_code,
                "procedure_id": procedure.identifier,
                "synthetic": "true",
                "lab": "lab01",
            },
        )
        created += 1
    return created, existing


def _add_procedure(
    memory: AgentMemoryAdapter,
    procedure: Any,
    *,
    scope: str,
    team_code: str,
    participant_code: str,
) -> tuple[int, int]:
    """Persist one selected synthetic procedure without duplicating a prior run."""

    if _memory_exists(memory, scope, procedure.content):
        return 0, 1
    memory.add_memory(
        procedure.content,
        memory_type="guideline",
        user_id=scope,
        agent_id=AGENT_ID,
        metadata={
            "team_code": team_code,
            "participant_code": participant_code,
            "procedure_id": procedure.identifier,
            "synthetic": "true",
            "lab": "lab01",
            "exercise_mode": "memory_only",
        },
    )
    return 1, 0


def _baseline_prompt(bundle: MemoryBundle) -> str:
    """Build the intentionally repetitive prompt used for a design-only comparison."""

    repeated = "\n".join(f"- {procedure.content}" for procedure in bundle.procedures)
    return f"Follow every procedure below.\n{repeated}\n\nQuestion: {bundle.primary_query}"


def _compact_prompt(bundle: MemoryBundle) -> str:
    """Build the compact prompt that relies on scoped retrieval."""

    return f"Use only retrieved team-scoped procedures.\n\nQuestion: {bundle.primary_query}"


def run_sdk_exercise(
    memory: AgentMemoryAdapter,
    bundle: MemoryBundle,
    *,
    team_code: str,
    participant_code: str,
    publish_to_team_scope: bool,
) -> SdkExerciseResult:
    """Persist and retrieve procedural memory through the real SDK adapter.

    The control phrase is intentionally searched only in the participant's own
    scope. A separate bootstrap operation stores that phrase in the control
    scope, so an empty result demonstrates scoped retrieval rather than an
    empty database.
    """

    scopes = build_team_scopes(team_code, participant_code)
    created, existing = _add_bundle(
        memory,
        bundle,
        scope=scopes.individual,
        team_code=team_code,
        participant_code=participant_code,
    )
    individual_results = list(
        memory.search(
            bundle.retrieval_query,
            user_id=scopes.individual,
            # The workshop stores procedural rules as ``guideline`` records.
            # Explicit filtering makes that distinction visible and prevents a
            # future message or profile record from being presented as a rule.
            record_types=["guideline"],
        )
    )
    cross_scope_results = list(
        memory.search(
            bundle.cross_team_challenge,
            user_id=scopes.individual,
            record_types=["guideline"],
        )
    )
    # ``list_memories`` is a direct SDK read of the durable store. It is the
    # persistence proof; keyword search is intentionally assessed separately
    # because a search can legitimately return fewer results than were stored.
    persisted_records = list(memory.list_memories(user_id=scopes.individual, limit=100))
    persisted_content = [_record_content(record) for record in persisted_records]

    shared_created = 0
    shared_existing = 0
    shared_results: list[Any] = []
    if publish_to_team_scope:
        shared_created, shared_existing = _add_bundle(
            memory,
            bundle,
            scope=scopes.shared,
            team_code=team_code,
            participant_code="shared",
        )
        shared_results = list(
            memory.search(
                bundle.retrieval_query,
                user_id=scopes.shared,
                record_types=["guideline"],
            )
        )

    retrieved_content = [_record_content(record) for record in individual_results]
    comparison = compare_prompt_usage(
        _baseline_prompt(bundle),
        _compact_prompt(bundle),
        retrieved_content,
    )
    evidence: dict[str, object] = {
        "active_team_id": team_code,
        "active_team_name": bundle.display_name,
        "algorithm": {
            "scope": scopes.individual,
            "query": bundle.retrieval_query,
            "max_results": len(individual_results),
            "record_types": ["guideline"],
        },
        "retrieved_procedure_ids": [
            procedure.identifier
            for procedure in bundle.procedures
            if procedure.content in retrieved_content
        ],
        "persisted_procedure_ids": [
            procedure.identifier
            for procedure in bundle.procedures
            if procedure.content in persisted_content
        ],
        "cross_team_challenge": bundle.cross_team_challenge,
        "cross_team_visible_procedure_ids": [],
        "isolation_passed": not cross_scope_results,
        "prompt_comparison": comparison.as_dict(),
        "evidence_type": "oci_sdk_execution_validation",
        "contains_no_secrets": True,
        "sdk_execution": {
            "schema_policy": "REQUIRE_EXISTING",
            "search_strategy": "KEYWORD",
            "individual_scope": scopes.individual,
            "team_shared_scope": scopes.shared,
            "control_scope": scopes.control,
            "individual_created": created,
            "individual_existing": existing,
            "team_shared_created": shared_created,
            "team_shared_existing": shared_existing,
            "team_shared_result_count": len(shared_results),
            "persistence_confirmed": all(
                procedure.content in persisted_content for procedure in bundle.procedures
            ),
        },
    }
    if not evidence["isolation_passed"]:
        evidence["cross_team_visible_procedure_ids"] = ["unexpected-cross-scope-result"]
    return SdkExerciseResult(evidence=evidence)


def run_memory_exercise(
    memory: AgentMemoryAdapter,
    bundle: MemoryBundle,
    *,
    team_code: str,
    participant_code: str,
    procedure_id: str,
) -> SdkExerciseResult:
    """Execute one real, no-inference memory exercise for a chosen safe rule.

    This deliberately uses the same participant scope, store policy, record type,
    and keyword strategy as the final token comparison. It does not construct an
    OCI Generative AI client and it never calls a model.
    """

    selected = next(
        (procedure for procedure in bundle.procedures if procedure.identifier == procedure_id),
        None,
    )
    if selected is None:
        available = ", ".join(procedure.identifier for procedure in bundle.procedures)
        raise ValueError(f"Unknown procedure_id '{procedure_id}'. Choose one of: {available}")

    retrieval_query_by_id = {
        "payment-idempotency": "idempotency",
        "contract-compatibility": "contract compatibility",
    }
    retrieval_query = retrieval_query_by_id.get(selected.identifier)
    if retrieval_query is None:
        raise ValueError(f"No approved keyword retrieval query exists for '{selected.identifier}'")

    scopes = build_team_scopes(team_code, participant_code)
    created, existing = _add_procedure(
        memory,
        selected,
        scope=scopes.individual,
        team_code=team_code,
        participant_code=participant_code,
    )
    retrieved_records = list(
        memory.search(
            retrieval_query,
            user_id=scopes.individual,
            record_types=["guideline"],
        )
    )
    retrieved_content = [_record_content(record) for record in retrieved_records]
    persisted_content = [
        _record_content(record)
        for record in memory.list_memories(user_id=scopes.individual, limit=100)
    ]
    cross_scope_results = list(
        memory.search(
            bundle.cross_team_challenge,
            user_id=scopes.individual,
            record_types=["guideline"],
        )
    )
    comparison = compare_prompt_usage(
        _baseline_prompt(bundle),
        _compact_prompt(bundle),
        retrieved_content,
    )
    persistence_confirmed = selected.content in persisted_content
    evidence: dict[str, object] = {
        "active_team_id": team_code,
        "active_team_name": bundle.display_name,
        "exercise_mode": "memory_only",
        "algorithm": {
            "scope": scopes.individual,
            "query": retrieval_query,
            "max_results": len(retrieved_records),
            "record_types": ["guideline"],
        },
        "selected_procedure_id": selected.identifier,
        "retrieved_procedure_ids": [
            procedure.identifier
            for procedure in bundle.procedures
            if procedure.content in retrieved_content
        ],
        "persisted_procedure_ids": [
            selected.identifier
        ] if persistence_confirmed else [],
        "cross_team_challenge": bundle.cross_team_challenge,
        "cross_team_visible_procedure_ids": [],
        "isolation_passed": not cross_scope_results,
        "prompt_comparison": comparison.as_dict(),
        "evidence_type": "oci_sdk_execution_validation",
        "contains_no_secrets": True,
        "sdk_execution": {
            "schema_policy": "REQUIRE_EXISTING",
            "search_strategy": "KEYWORD",
            "individual_scope": scopes.individual,
            "team_shared_scope": scopes.shared,
            "control_scope": scopes.control,
            "individual_created": created,
            "individual_existing": existing,
            "team_shared_created": 0,
            "team_shared_existing": 0,
            "team_shared_result_count": 0,
            "persistence_confirmed": persistence_confirmed,
        },
    }
    if not evidence["isolation_passed"]:
        evidence["cross_team_visible_procedure_ids"] = ["unexpected-cross-scope-result"]
    return SdkExerciseResult(evidence=evidence)
