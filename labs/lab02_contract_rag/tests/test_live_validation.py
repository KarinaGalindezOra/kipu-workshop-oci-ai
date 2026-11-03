"""Unit tests for Lab 2 live-runner safeguards without OCI calls."""

from __future__ import annotations

import pytest
from lab02_contract_rag.live_validation import (
    chunks_to_insert,
    grounded_prompt,
    validated_table_name,
)
from lab02_contract_rag.models import ContractChunk, RetrievedEvidence


def synthetic_chunk(content_hash: str = "a" * 64) -> ContractChunk:
    """Create a small source-traceable chunk for runner tests."""

    return ContractChunk(
        chunk_id="v2-01-example",
        contract_version="v2",
        source_uri="synthetic://contracts/contract_v2.md",
        section="Migration from v1",
        content="Rename payment_status to status.",
        content_hash=content_hash,
    )


def test_validated_table_name_rejects_sql_syntax() -> None:
    """The dynamic table identifier cannot carry injected SQL."""

    assert validated_table_name("LAB02_CONTRACT_CHUNKS") == "LAB02_CONTRACT_CHUNKS"
    with pytest.raises(RuntimeError, match="simple identifier"):
        validated_table_name("LAB02_CONTRACT_CHUNKS; DROP TABLE USERS")


def test_chunks_to_insert_only_returns_missing_content() -> None:
    """An existing equal hash is reused without an update."""

    chunk = synthetic_chunk()
    assert chunks_to_insert([chunk], {chunk.chunk_id: chunk.content_hash}) == []
    assert chunks_to_insert([chunk], {}) == [chunk]


def test_chunks_to_insert_rejects_a_content_collision() -> None:
    """A chunk identifier with different content stops the runner."""

    chunk = synthetic_chunk()
    with pytest.raises(RuntimeError, match="Refusing to replace"):
        chunks_to_insert([chunk], {chunk.chunk_id: "b" * 64})


def test_grounded_prompt_contains_only_retrieved_content() -> None:
    """The model prompt includes the selected evidence and the question."""

    chunk = synthetic_chunk()
    prompt = grounded_prompt(
        "How should the client migrate?", [RetrievedEvidence(chunk=chunk, score=0.02)]
    )
    assert "How should the client migrate?" in prompt
    assert chunk.content in prompt
    assert "Insufficient evidence." in prompt
