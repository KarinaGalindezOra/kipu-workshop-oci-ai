"""Developer-only offline regression; not an accepted Workshop 2 execution path."""

import argparse
import os
from pathlib import Path

from .agent import run_agent
from .corpus import load_corpus
from .participant import artifact_directory, participant_id
from .reporting import write_result
from .retrieval import retrieve

DEFAULT_QUESTION = "How must a client update the endpoint when migrating from v1 to v2?"


def contract_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def load_chunks() -> list:
    return load_corpus()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--contract-version")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab02"))
    parser.add_argument(
        "--participant-id", type=participant_id, default=os.getenv("LAB02_PARTICIPANT_ID", "p001")
    )
    args = parser.parse_args()
    chunks = load_chunks()
    result = run_agent(
        args.question,
        lambda v, q: retrieve(chunks, q, v),
        version=args.contract_version,
        compare=args.compare,
    )
    result["participant_id"] = args.participant_id
    output = artifact_directory(args.output_dir, args.participant_id, result["run_id"])
    write_result(output, result)
    print(f"STATUS {result['status']}")
    print(f"VERSION_FILTER_PASS {result['version_filter_pass']}")
    print(f"EVIDENCE_REPORT {output / 'lab02-evidence.json'}")
    if result["status"] == "error":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
