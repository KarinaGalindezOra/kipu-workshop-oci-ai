"""Run the local build-and-test phase of the Lab 1 participant exercise."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .metrics import compare_prompt_usage
from .models import Guideline, MemoryScope
from .store import ScopedMemoryStore

AGENT_ID = "khipu-workshop-agent"
THREAD_ID = "lab01-hands-on"


@dataclass(frozen=True)
class MemoryBundle:
    """Represent a team-owned, deployable procedural memory bundle."""

    team_id: str
    display_name: str
    procedures: tuple[Guideline, ...]
    primary_query: str
    retrieval_query: str
    cross_team_challenge: str
    required_response_terms: tuple[str, ...]


def _required_string(payload: dict[str, Any], name: str) -> str:
    """Return a non-empty string field or raise a useful bundle error."""

    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Bundle field '{name}' must be a non-empty string")
    return value.strip()


def load_bundle(path: Path) -> MemoryBundle:
    """Load and validate a synthetic workshop memory bundle from JSON."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Bundle file was not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Bundle is not valid JSON: {path}") from error

    if not isinstance(payload, dict):
        raise ValueError("Bundle root must be a JSON object")
    required_terms_payload = payload.get("required_response_terms")
    valid_required_terms = isinstance(required_terms_payload, list) and all(
        isinstance(term, str) and term.strip() for term in required_terms_payload
    )
    if not valid_required_terms:
        raise ValueError("Bundle field 'required_response_terms' must be a non-empty array")
    procedures_payload = payload.get("procedures")
    if not isinstance(procedures_payload, list) or not procedures_payload:
        raise ValueError("Bundle field 'procedures' must be a non-empty array")

    procedures: list[Guideline] = []
    for entry in procedures_payload:
        if not isinstance(entry, dict):
            raise ValueError("Every procedure must be a JSON object")
        tags = entry.get("tags", [])
        valid_tags = isinstance(tags, list) and all(
            isinstance(tag, str) and tag.strip() for tag in tags
        )
        if not valid_tags:
            raise ValueError("Procedure tags must be an array of non-empty strings")
        procedures.append(
            Guideline(
                identifier=_required_string(entry, "id"),
                content=_required_string(entry, "content"),
                tags=tuple(tag.strip() for tag in tags),
            )
        )

    return MemoryBundle(
        team_id=_required_string(payload, "team_id"),
        display_name=_required_string(payload, "display_name"),
        procedures=tuple(procedures),
        primary_query=_required_string(payload, "primary_query"),
        retrieval_query=_required_string(payload, "retrieval_query"),
        cross_team_challenge=_required_string(payload, "cross_team_challenge"),
        required_response_terms=tuple(term.strip() for term in required_terms_payload),
    )


def _scope(team_id: str) -> MemoryScope:
    """Create the exact team scope used by the local retrieval adapter."""

    return MemoryScope(team_id=team_id, agent_id=AGENT_ID, thread_id=THREAD_ID)


def retrieve_team_memory(store: ScopedMemoryStore, team_id: str, query: str) -> list[Guideline]:
    """Retrieve procedures only from the caller's explicit team scope."""

    return store.search(_scope(team_id), query)


def _baseline_prompt(question: str, procedures: tuple[Guideline, ...]) -> str:
    """Build the intentionally inefficient prompt that repeats all procedures."""

    repeated_rules = "\n".join(f"- {procedure.content}" for procedure in procedures)
    return f"Follow every procedure below.\n{repeated_rules}\n\nQuestion: {question}"


def _compact_prompt(question: str) -> str:
    """Build the prompt that expects relevant procedures to be retrieved separately."""

    return f"Use only retrieved team-scoped procedures.\n\nQuestion: {question}"


def build_participant_report(
    active_bundle: MemoryBundle,
    other_bundle: MemoryBundle,
) -> dict[str, object]:
    """Execute the local algorithm and return safe evidence for the participant."""

    if active_bundle.team_id == other_bundle.team_id:
        raise ValueError("The active and comparison bundles must use distinct team_id values")

    store = ScopedMemoryStore()
    for procedure in active_bundle.procedures:
        store.add_guideline(_scope(active_bundle.team_id), procedure)
    for procedure in other_bundle.procedures:
        store.add_guideline(_scope(other_bundle.team_id), procedure)

    retrieved = retrieve_team_memory(store, active_bundle.team_id, active_bundle.retrieval_query)
    cross_team_visible = retrieve_team_memory(
        store,
        active_bundle.team_id,
        active_bundle.cross_team_challenge,
    )
    all_procedures = active_bundle.procedures + other_bundle.procedures
    comparison = compare_prompt_usage(
        _baseline_prompt(active_bundle.primary_query, all_procedures),
        _compact_prompt(active_bundle.primary_query),
        [procedure.content for procedure in retrieved],
    )
    return {
        "active_team_id": active_bundle.team_id,
        "active_team_name": active_bundle.display_name,
        "algorithm": {
            "scope": active_bundle.team_id,
            "query": active_bundle.retrieval_query,
            "max_results": len(retrieved),
        },
        "retrieved_procedure_ids": [procedure.identifier for procedure in retrieved],
        "cross_team_challenge": active_bundle.cross_team_challenge,
        "cross_team_visible_procedure_ids": [
            procedure.identifier for procedure in cross_team_visible
        ],
        "isolation_passed": not cross_team_visible,
        "prompt_comparison": comparison.as_dict(),
        "evidence_type": "local_algorithm_validation",
        "contains_no_secrets": True,
    }


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the participant exercise."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        required=True,
        type=Path,
        help="Active team memory bundle JSON",
    )
    parser.add_argument(
        "--other-bundle",
        required=True,
        type=Path,
        help="Comparison team memory bundle JSON",
    )
    parser.add_argument("--output-path", type=Path, help="Optional safe JSON evidence output")
    return parser.parse_args()


def main() -> None:
    """Run the exercise and print a readable, safe result."""

    args = _parse_args()
    report = build_participant_report(load_bundle(args.bundle), load_bundle(args.other_bundle))
    if args.output_path:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("LAB01_LOCAL_ALGORITHM_READY")
    print("ACTIVE_TEAM", report["active_team_id"])
    print("RETRIEVED_PROCEDURES", ",".join(report["retrieved_procedure_ids"]) or "none")
    print("CROSS_TEAM_VISIBLE", ",".join(report["cross_team_visible_procedure_ids"]) or "none")
    print("ISOLATION_PASS", report["isolation_passed"])
    print("TOKEN_REDUCTION", report["prompt_comparison"]["estimated_request_reduction_tokens"])
    if args.output_path:
        print("EVIDENCE_PATH", args.output_path)


if __name__ == "__main__":
    main()
