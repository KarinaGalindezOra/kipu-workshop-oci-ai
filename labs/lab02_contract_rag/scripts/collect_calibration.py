"""Collect development distances after approved ingestion; makes paid embedding calls."""

import argparse
import json
import os
from dataclasses import replace
from pathlib import Path

from lab02_contract_rag.corpus import LAB_ROOT
from lab02_contract_rag.live_validation import (
    create_database_connection,
    create_inference_client,
    embed_texts,
    retrieve_evidence,
    settings_from_environment,
)
from lab02_contract_rag.private_session import add_session_file_argument, load_participant_session

parser = argparse.ArgumentParser(description=__doc__)
add_session_file_argument(parser)
parser.add_argument("--confirm-live-inference", action="store_true")
parser.add_argument("--output", type=Path)
args = parser.parse_args()
if not args.confirm_live_inference:
    parser.error("Development measurements require approved budget and live acknowledgement")
load_participant_session(args.session_file)
if args.output is None:
    configured = os.getenv("LAB02_DEVELOPMENT_MEASUREMENTS_FILE")
    if not configured:
        parser.error("Provide --output or configure LAB02_DEVELOPMENT_MEASUREMENTS_FILE privately")
    args.output = Path(configured)
try:
    settings = replace(settings_from_environment(require_calibration=False), max_cosine_distance=2)
    client = create_inference_client(settings)
    questions = json.loads((LAB_ROOT / "data/evaluation/development_questions.json").read_text())
    rows = []
    with create_database_connection(settings) as connection, connection.cursor() as cursor:
        for item in questions:
            version = "v1" if "v1" in item["question"] else "v2"
            vector = embed_texts(client, settings, [item["question"]], "SEARCH_QUERY")[0]
            evidence = retrieve_evidence(cursor, settings.table_name, version, vector, 3, settings)
            for candidate in evidence:
                rows.append(
                    {
                        "question_id": item["id"],
                        "distance": candidate.score,
                        "relevant": candidate.chunk.section == item["relevant_section"],
                    }
                )
    payload = {
        "context": {
            "corpus_id": "contracts-baseline-02-es",
            "region": settings.region,
            "model_id": settings.embedding_model_id,
            "dimension": settings.vector_dimension,
        },
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("DEVELOPMENT_MEASUREMENTS_WRITTEN; keep configuration private")
except Exception:
    raise SystemExit(
        "Calibration collection failed; inspect connectivity and model approval"
    ) from None
