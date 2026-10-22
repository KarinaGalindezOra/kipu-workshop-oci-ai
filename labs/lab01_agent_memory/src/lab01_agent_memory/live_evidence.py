"""Safe evidence contracts for the facilitator's live OCI validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"


def create_live_evidence(
    *,
    team_a_result_count: int,
    team_a_isolation_passed: bool,
    team_b_result_count: int,
    team_b_isolation_passed: bool,
) -> dict[str, object]:
    """Create a safe, portable view of an OCI isolation validation result."""

    evidence = {
        "schema_version": SCHEMA_VERSION,
        "evidence_type": "lab01_oci_isolation_validation",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "contains_no_secrets": True,
        "teams": {
            "team-a": {
                "result_count": team_a_result_count,
                "isolation_passed": team_a_isolation_passed,
            },
            "team-b": {
                "result_count": team_b_result_count,
                "isolation_passed": team_b_isolation_passed,
            },
        },
    }
    return validate_live_evidence(evidence)


def validate_live_evidence(evidence: Mapping[str, Any]) -> dict[str, object]:
    """Validate the portable evidence structure before it reaches the UI."""

    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported Lab 1 evidence schema: {evidence.get('schema_version')!r}")
    if evidence.get("evidence_type") != "lab01_oci_isolation_validation":
        raise ValueError("Unexpected Lab 1 evidence type")
    if evidence.get("contains_no_secrets") is not True:
        raise ValueError("Live evidence must explicitly confirm it contains no secrets")

    teams = evidence.get("teams")
    if not isinstance(teams, Mapping):
        raise ValueError("Live evidence teams must be an object")

    normalized_teams: dict[str, dict[str, object]] = {}
    for team_id in ("team-a", "team-b"):
        result = teams.get(team_id)
        if not isinstance(result, Mapping):
            raise ValueError(f"Live evidence is missing {team_id}")
        count = result.get("result_count")
        passed = result.get("isolation_passed")
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"{team_id} result_count must be a non-negative integer")
        if not isinstance(passed, bool):
            raise ValueError(f"{team_id} isolation_passed must be a boolean")
        normalized_teams[team_id] = {"result_count": count, "isolation_passed": passed}

    generated_at = evidence.get("generated_at_utc")
    if not isinstance(generated_at, str) or not generated_at:
        raise ValueError("Live evidence requires generated_at_utc")

    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_type": "lab01_oci_isolation_validation",
        "generated_at_utc": generated_at,
        "contains_no_secrets": True,
        "teams": normalized_teams,
    }


def write_live_evidence(evidence: Mapping[str, Any], output_path: Path) -> Path:
    """Write validated evidence without credentials or database connection details."""

    validated = validate_live_evidence(evidence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
    return output_path


def load_live_evidence(raw_json: str) -> dict[str, object]:
    """Load a facilitator-provided evidence file for display in the participant UI."""

    try:
        value = json.loads(raw_json)
    except json.JSONDecodeError as error:
        raise ValueError("The selected evidence file is not valid JSON") from error
    if not isinstance(value, Mapping):
        raise ValueError("The selected evidence file must contain an object")
    return validate_live_evidence(value)
