"""Calibrate an upper cosine-distance bound from development measurements only."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from .corpus import LAB_ROOT

CANDIDATE_DISTANCE_MARGIN = 0.02


def development_hash() -> str:
    return hashlib.sha256(
        (LAB_ROOT / "data/evaluation/development_questions.json").read_bytes()
    ).hexdigest()


def calibrate(measurements: dict) -> dict:
    expected = {
        item["id"]
        for item in json.loads(
            (LAB_ROOT / "data/evaluation/development_questions.json").read_text()
        )
    }
    rows = measurements["rows"]
    if {r["question_id"] for r in rows} != expected:
        raise ValueError("Use the entire development set, never acceptance questions")
    if any(
        not isinstance(r["relevant"], bool)
        or not math.isfinite(r["distance"])
        or not 0 <= r["distance"] <= 2
        for r in rows
    ):
        raise ValueError("Invalid labeled distance")
    positive = [r["distance"] for r in rows if r["relevant"]]
    negative = [r["distance"] for r in rows if not r["relevant"]]
    if not positive or not negative:
        raise ValueError("Development measurements require both supported and unsupported cases")
    context = measurements["context"]
    if set(context) != {"corpus_id", "region", "model_id", "dimension"}:
        raise ValueError("Calibration context is incomplete")
    max_positive = max(positive)
    min_negative = min(negative)
    return {
        "context": context,
        "development_sha256": development_hash(),
        # Candidate distance is not evidence. A small margin preserves positive recall;
        # evidence selection and claim validation reject unrelated neighbors.
        "max_cosine_distance": min(1.999, max_positive + CANDIDATE_DISTANCE_MARGIN),
        "max_positive_distance": max_positive,
        "min_negative_distance": min_negative,
        "negative_overlap_detected": max_positive >= min_negative,
        "evidence_selection_required": True,
        "measurement_sha256": hashlib.sha256(
            json.dumps(measurements, sort_keys=True).encode()
        ).hexdigest(),
    }


def validate_calibration(path: Path, *, region: str, model_id: str, dimension: int) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["context"] != {
        "corpus_id": "contracts-baseline-02-es",
        "region": region,
        "model_id": model_id,
        "dimension": dimension,
    }:
        raise ValueError("Calibration context does not match the active embedding space")
    value = payload["max_cosine_distance"]
    if payload["development_sha256"] != development_hash() or not 0 < value < 2:
        raise ValueError("Calibration is stale or invalid")
    if payload.get("evidence_selection_required") is False:
        raise ValueError("Calibration cannot disable evidence selection")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = calibrate(json.loads(args.measurements.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("CALIBRATION_WRITTEN; keep this configuration private")


if __name__ == "__main__":
    main()
