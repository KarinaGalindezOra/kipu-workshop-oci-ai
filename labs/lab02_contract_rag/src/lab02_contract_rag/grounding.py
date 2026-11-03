"""Application-side evidence attachment for grounded contract answers."""

from __future__ import annotations

from .models import RetrievedEvidence


def attach_evidence(answer: str, evidence: list[RetrievedEvidence]) -> dict[str, object]:
    """Return an answer envelope whose citations come from retrieved metadata.

    The application, not the language model, owns version, source, and section
    citations. This prevents a model formatting variation from removing
    traceability from an otherwise grounded answer.
    """

    if not evidence or answer.strip().lower() in {
        "insufficient evidence.",
        "insufficient evidence",
    }:
        return {
            "answer": "Insufficient evidence.",
            "sufficient_evidence": False,
            "evidence": [],
        }

    return {
        "answer": answer.strip(),
        "sufficient_evidence": False,
        "support_assessment": "unverified_legacy_attachment",
        "evidence": [
            {
                "chunk_id": item.chunk.chunk_id,
                "contract_version": item.chunk.contract_version,
                "source_uri": item.chunk.source_uri,
                "section": item.chunk.section,
                "content_hash": item.chunk.content_hash,
            }
            for item in evidence
        ],
    }
