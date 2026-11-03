"""Write manifest-verified local chunks without network access."""

import argparse
import json
import os
from dataclasses import asdict, replace
from datetime import UTC, datetime
from pathlib import Path

from lab02_contract_rag.corpus import load_corpus
from lab02_contract_rag.participant import artifact_directory, participant_id

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab02/local-corpus"))
parser.add_argument(
    "--participant-id", type=participant_id, default=os.getenv("LAB02_PARTICIPANT_ID", "p001")
)
args = parser.parse_args()
chunks = [asdict(replace(c, loaded_at=datetime.now(UTC).isoformat())) for c in load_corpus()]
output = artifact_directory(args.output_dir, args.participant_id)
output.mkdir(parents=True, exist_ok=True)
(output / "chunks.json").write_text(
    json.dumps({"participant_id": args.participant_id, "chunks": chunks}, indent=2),
    encoding="utf-8",
)
print(f"CHUNK_COUNT {len(chunks)}")
