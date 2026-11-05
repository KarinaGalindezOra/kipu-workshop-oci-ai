"""Offline participant exercises for corpus inspection and lexical retrieval."""

from __future__ import annotations

import json
from pathlib import Path

from .agent import run_agent
from .corpus import LAB_ROOT, load_corpus
from .reporting import write_result
from .retrieval import retrieve


def workshop_case(case_id: str) -> dict:
    """Return one immutable public workshop case by identifier."""

    cases = json.loads(
        (LAB_ROOT / "data/evaluation/workshop_questions.json").read_text(encoding="utf-8")
    )
    case = next((item for item in cases if item["id"] == case_id.upper()), None)
    if case is None:
        raise ValueError(f"Unknown workshop case: {case_id}")
    return case


def corpus_inspection() -> dict:
    """Return report-safe metadata for the frozen local corpus without network access."""

    chunks = load_corpus()
    return {
        "mode": "local_corpus_inspection",
        "network_access": False,
        "chunk_count": len(chunks),
        "corpus_id": chunks[0].corpus_id,
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "contract_version": chunk.contract_version,
                "section": chunk.section,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "source_uri": chunk.source_uri,
                "content_hash": chunk.content_hash,
                "document_hash": chunk.document_hash,
            }
            for chunk in chunks
        ],
    }


def local_case_result(case_id: str, participant_id: str) -> dict:
    """Run deterministic lexical retrieval and extractive evidence selection for a workshop case."""

    case = workshop_case(case_id)
    chunks = load_corpus()
    result = run_agent(
        case["question"],
        lambda version, question: retrieve(chunks, question, version),
        compare=len(case["versions"]) > 1,
    )
    result.update(
        case_id=case["id"],
        participant_id=participant_id,
        practice_mode="local_lexical_retrieval",
        execution_origin="local_practice",
        cloud_validation="not_run",
        fixture_simulated=False,
    )
    return result


def write_inspection(output_dir: Path, inspection: dict) -> Path:
    """Persist an offline inspection report in the participant artifact namespace."""

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "corpus-inspection.json"
    path.write_text(json.dumps(inspection, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_local_case(output_dir: Path, result: dict) -> Path:
    """Persist a local practice report that cannot be mistaken for OCI validation."""

    return write_result(output_dir, result)
