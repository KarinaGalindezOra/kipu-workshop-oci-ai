"""Run safe offline corpus-inspection and lexical-retrieval exercises for Workshop 2."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from lab02_contract_rag.local_practice import (
    corpus_inspection,
    local_case_result,
    write_inspection,
    write_local_case,
)
from lab02_contract_rag.participant import artifact_directory, participant_id
from lab02_contract_rag.private_session import add_session_file_argument, load_participant_session


def build_parser() -> argparse.ArgumentParser:
    """Build the participant-safe command-line interface."""

    parser = argparse.ArgumentParser(description=__doc__)
    add_session_file_argument(parser)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab02/local-practice"))
    parser.add_argument("--participant-id", default=None)
    subcommands = parser.add_subparsers(dest="activity", required=True)
    subcommands.add_parser("inspect", help="Inspect nine manifest-verified local chunks without OCI.")
    retrieve_parser = subcommands.add_parser(
        "retrieve", help="Run local lexical retrieval and evidence selection without OCI."
    )
    retrieve_parser.add_argument("--case-id", required=True, help="Public workshop case, for example T03.")
    return parser


def main(argv: list[str] | None = None) -> None:
    """Execute one local practice activity; no OCI call is made."""

    args = build_parser().parse_args(argv)
    load_participant_session(args.session_file)
    assigned_id = participant_id(args.participant_id or os.getenv("LAB02_PARTICIPANT_ID", "p001"))
    output = artifact_directory(args.output_dir, assigned_id)

    if args.activity == "inspect":
        inspection = corpus_inspection()
        report = write_inspection(output, inspection)
        print("ACTIVITY inspeccion_local")
        print("OCI_EXECUTED False")
        print(f"CHUNK_COUNT {inspection['chunk_count']}")
        print(f"CORPUS_REPORT {report}")
        return

    result = local_case_result(args.case_id, assigned_id)
    report = write_local_case(output, result)
    print("ACTIVITY recuperacion_lexica_local")
    print("OCI_EXECUTED False")
    print(f"CASE_ID {result['case_id']}")
    print(f"STATUS {result['status']}")
    print(f"CANDIDATE_COUNT {len(result['candidates'])}")
    print(f"EVIDENCE_REPORT {report}")


if __name__ == "__main__":
    main()
