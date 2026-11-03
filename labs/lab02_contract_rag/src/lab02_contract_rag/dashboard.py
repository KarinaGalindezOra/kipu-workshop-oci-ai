"""Participant-bound report access and expected-versus-observed assessment."""

import json
from pathlib import Path

from .corpus import LAB_ROOT
from .evaluation import grade
from .participant import participant_id


def workshop_cases() -> list[dict]:
    cases = json.loads(
        (LAB_ROOT / "data/evaluation/workshop_questions.json").read_text(encoding="utf-8")
    )
    if any(c.get("fixture") for c in cases):
        raise ValueError("Simulated cases cannot enter the real workshop")
    return cases


def expected_comparison(result: dict) -> dict | None:
    cases = workshop_cases()
    case_id = result.get("case_id")
    case = (
        next((item for item in cases if item["id"] == case_id), None)
        if isinstance(case_id, str)
        else next((item for item in cases if item["question"] == result.get("question")), None)
    )
    if case is None or case["question"] != result.get("question"):
        return None
    controls = result.get("request_controls", {})
    version = controls.get("version")
    if version is not None and version not in case["versions"]:
        return None
    if controls.get("compare") and len(case["versions"]) < 2:
        return None
    return {"case": case, "assessment": grade(case, result), "human_review_required": True}


def candidate_selection(result: dict) -> tuple[list[dict], dict[str, dict]]:
    """Annotate retrieved candidates with their publication as accepted evidence."""
    candidates = result.get("candidates", [])
    citations = result.get("citations", [])
    if not isinstance(candidates, list) or not isinstance(citations, list):
        return [], {}
    selected_chunk_ids = {
        source.get("chunk_id")
        for source in citations
        if isinstance(source, dict) and isinstance(source.get("chunk_id"), str)
    }
    rows = []
    by_chunk = {}
    for candidate in candidates:
        if not isinstance(candidate, dict) or not isinstance(candidate.get("chunk_id"), str):
            continue
        by_chunk[candidate["chunk_id"]] = candidate
        rows.append({**candidate, "selected_as_evidence": candidate["chunk_id"] in selected_chunk_ids})
    return rows, by_chunk


def participant_root(root: Path, assigned_id: str) -> Path:
    root = root.resolve()
    own = root / participant_id(assigned_id)
    if own.resolve() != own:
        raise ValueError("Participant directory cannot redirect to another location")
    return own


def load_own_report(root: Path, assigned_id: str, path: Path) -> dict:
    own = participant_root(root, assigned_id)
    resolved = path.resolve()
    if not resolved.is_relative_to(own) or resolved.name != "lab02-evidence.json":
        raise ValueError("Report is outside this participant's namespace")
    if resolved.stat().st_size > 4_000_000:
        raise ValueError("Report exceeds the dashboard size limit")
    result = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("Evidence report must be a JSON object")
    if (
        result.get("participant_id") != assigned_id
        or result.get("mode") != "oci"
        or result.get("execution_origin") not in {"oci_services", "application_control"}
        or result.get("fixture_simulated") is not False
    ):
        raise ValueError("Only this participant's real-workflow reports are accepted")
    if not isinstance(result.get("claims"), list) or not isinstance(result.get("citations"), list):
        raise ValueError("Malformed evidence report")
    for field in ("question", "answer", "status"):
        if not isinstance(result.get(field), str):
            raise ValueError("Report text fields are malformed")
    if not isinstance(result.get("service_trace"), list):
        raise ValueError("Report is missing service provenance")
    return result


def list_own_reports(root: Path, assigned_id: str) -> list[Path]:
    own = participant_root(root, assigned_id)
    found = []
    for path in own.glob("*/lab02-evidence.json"):
        try:
            load_own_report(root, assigned_id, path)
            found.append(path)
        except (ValueError, OSError, KeyError, TypeError):
            continue
    return sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)
