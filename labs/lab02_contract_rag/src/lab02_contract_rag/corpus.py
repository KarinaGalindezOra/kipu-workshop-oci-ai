"""Load only the immutable, manifest-verified synthetic corpus."""

import hashlib
import json
from pathlib import Path

from .chunking import chunk_contract
from .models import ContractChunk

LAB_ROOT = Path(__file__).resolve().parents[2]


def load_corpus(data_dir: Path | None = None) -> list[ContractChunk]:
    data_dir = data_dir or LAB_ROOT / "data"
    manifest = json.loads((data_dir / "corpus_manifest.json").read_text(encoding="utf-8"))
    chunks = []
    for entry in manifest["documents"]:
        name = entry["file"]
        if name not in {"contract_v1.md", "contract_v2.md"}:
            raise ValueError("Manifest contains an unapproved source")
        raw = (data_dir / name).read_bytes()
        canonical = raw.replace(b"\r\n", b"\n")
        if hashlib.sha256(canonical).hexdigest() != entry["sha256"]:
            raise ValueError("Source bytes do not match the frozen corpus manifest")
        text = raw.decode("utf-8").replace("\r\n", "\n")
        items = chunk_contract(f"synthetic://contracts/{name}", text, manifest["corpus_id"])
        if len(items) != entry["chunk_count"] or any(
            c.contract_version != entry["contract_version"] for c in items
        ):
            raise ValueError("Source metadata does not match manifest")
        chunks.extend(items)
    if len(chunks) != 9 or len({c.chunk_id for c in chunks}) != 9:
        raise ValueError("Expected nine unique baseline chunks")
    return chunks
