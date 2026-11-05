"""Deterministic lexical retrieval used before the OCI vector-search integration."""

from __future__ import annotations

import re

from .models import ContractChunk, RetrievedEvidence

TOKEN_PATTERN = re.compile(r"[\w/-]+", re.UNICODE)


def tokens(value: str) -> set[str]:
    """Normalize retrieval terms without external model dependencies."""

    return set(TOKEN_PATTERN.findall(value.lower()))


def retrieve(
    chunks: list[ContractChunk],
    question: str,
    contract_version: str,
    limit: int = 3,
    *,
    corpus_id: str = "contracts-baseline-02-es",
    api_name: str = "disbursement",
) -> list[RetrievedEvidence]:
    """Filter by version first, then rank chunks by lexical token overlap."""

    question_tokens = tokens(question) - {"v1", "v2", "v3"}
    if not 1 <= limit <= 3:
        raise ValueError("Retrieval limit must be between 1 and 3")
    evidence = [
        RetrievedEvidence(
            chunk=chunk,
            score=(
                2 * len(question_tokens & tokens(chunk.section))
                + len(question_tokens & tokens(chunk.content))
            ),
        )
        for chunk in chunks
        if chunk.contract_version == contract_version
        and chunk.corpus_id == corpus_id
        and chunk.api_name == api_name
        and chunk.data_classification == "synthetic"
    ]
    ranked = sorted(evidence, key=lambda item: (-item.score, item.chunk.chunk_id))
    return [item for item in ranked if item.score > 0][:limit]
