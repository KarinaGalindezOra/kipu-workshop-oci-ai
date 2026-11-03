"""Evidence reports for the Lab 2 offline RAG exercise."""

from __future__ import annotations

import json
from pathlib import Path

from .models import RetrievedEvidence


def json_safe(value):
    """Return report-safe JSON values without serializing provider implementation objects.

    OCI SDK usage metadata is informational only.  A new SDK field must never make a
    validated workshop answer disappear merely because it is not JSON serializable.
    Unknown values are represented by their type, never by their string value.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return {"unavailable_value_type": type(value).__name__}


def write_evidence(
    output_dir: Path, question: str, version: str, evidence: list[RetrievedEvidence]
) -> None:
    """Persist a machine-readable and facilitator-friendly retrieval record."""

    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "question": question,
        "requested_contract_version": version,
        "evidence_count": len(evidence),
        "report_version": "2.0",
        "sufficient_evidence": False,
        "support_assessment": "not_assessed_by_retrieval_report",
        "evidence": [
            {
                "chunk_id": item.chunk.chunk_id,
                "score": item.score,
                "contract_version": item.chunk.contract_version,
                "source_uri": item.chunk.source_uri,
                "section": item.chunk.section,
                "content_hash": item.chunk.content_hash,
            }
            for item in evidence
        ],
    }
    (output_dir / "lab02-evidence.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Lab 2 Retrieval Evidence",
        "",
        f"Question: {question}",
        f"Requested contract version: {version}",
        f"Evidence count: {len(evidence)}",
        "",
    ]
    if evidence:
        lines.extend(["| Version | Section | Source | Score |", "| --- | --- | --- | ---: |"])
        lines.extend(
            f"| {item.chunk.contract_version} | {item.chunk.section} | "
            f"{item.chunk.source_uri} | {item.score} |"
            for item in evidence
        )
    else:
        lines.append("Insufficient evidence: no retrieved chunk supports the requested answer.")
    (output_dir / "lab02-evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_result(output_dir: Path, result: dict) -> Path:
    """Persist the validated result, not the unverified model draft."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "lab02-evidence.json"
    path.write_text(json.dumps(json_safe(result), indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Lab 2 evidence",
        "",
        f"Status: {result['status']}",
        "",
        result["answer"],
        "",
        "## Citations",
        "",
    ]
    for item in result["citations"]:
        lines.extend([f"- [{item['label']}]({item['source_uri']})", "", f"> {item['excerpt']}", ""])
    lines.extend(["## Limitations", "", *result["limitations"]])
    path.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    return path
