"""Deterministic Markdown section chunking for the offline Lab 2 exercise."""

from __future__ import annotations

import hashlib
import re

from .models import ContractChunk

VERSION_PATTERN = re.compile(r"^(?:Contract Version|Versión del contrato):\s*(v\d+)\s*$", re.MULTILINE)
SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def contract_version(markdown: str) -> str:
    """Extract the declared contract version from a workshop document."""

    match = VERSION_PATTERN.search(markdown)
    if not match:
        raise ValueError("Contract document does not declare a version")
    return match.group(1)


def chunk_contract(
    source_uri: str, markdown: str, corpus_id: str = "contracts-baseline-02-es"
) -> list[ContractChunk]:
    """Split each level-two heading into a single source-traceable chunk."""

    version = contract_version(markdown)
    declarations = VERSION_PATTERN.findall(markdown)
    if len(declarations) != 1 or version not in {"v1", "v2"}:
        raise ValueError("Contract must declare exactly one supported version")
    title = markdown.splitlines()[0].removeprefix("# ").strip()
    document_hash = hashlib.sha256(markdown.encode()).hexdigest()
    matches = list(SECTION_PATTERN.finditer(markdown))
    if not matches:
        raise ValueError("Contract document does not contain sections")

    chunks: list[ContractChunk] = []
    for index, match in enumerate(matches, start=1):
        end = matches[index].start() if index < len(matches) else len(markdown)
        content = markdown[match.end() : end].strip()
        if not content:
            continue
        source_key = f"{corpus_id}|{source_uri}|{version}|{match.group(1)}|{content}".encode()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        chunks.append(
            ContractChunk(
                chunk_id=f"{version}-{index:02d}-{hashlib.sha256(source_key).hexdigest()[:10]}",
                contract_version=version,
                source_uri=source_uri,
                section=match.group(1),
                content=content,
                content_hash=content_hash,
                corpus_id=corpus_id,
                document_id=f"disbursement-contract-{version}",
                source_title=title,
                line_start=markdown.count("\n", 0, match.start()) + 1,
                line_end=markdown[:end].rstrip().count("\n") + 1,
                document_hash=document_hash,
                embedding_input_hash=content_hash,
            )
        )
    return chunks
