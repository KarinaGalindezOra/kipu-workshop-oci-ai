"""Domain models for versioned contract retrieval evidence."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractChunk:
    """A source-grounded contract section prepared for retrieval."""

    chunk_id: str
    contract_version: str
    source_uri: str
    section: str
    content: str
    content_hash: str
    corpus_id: str = "contracts-baseline-01"
    document_id: str = ""
    api_name: str = "disbursement"
    source_title: str = ""
    document_type: str = "api_contract"
    subsection: str | None = None
    line_start: int = 0
    line_end: int = 0
    effective_from: str | None = None
    data_classification: str = "synthetic"
    document_hash: str = ""
    embedding: tuple[float, ...] | None = None
    embedding_model_id: str | None = None
    embedding_dimension: int | None = None
    embedding_input_hash: str = ""
    chunking_version: str = "heading-v1"
    loaded_at: str | None = None


@dataclass(frozen=True)
class RetrievedEvidence:
    """A ranked chunk that can support a grounded answer."""

    chunk: ContractChunk
    score: float
    method: str = "lexical"
    score_type: str = "token_overlap"
