"""Tests for the participant-local calibration command helpers."""

import importlib.util
import json
from pathlib import Path

import pytest
from lab02_contract_rag.calibration import calibrate

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "calibrate_participant.py"
)
SPEC = importlib.util.spec_from_file_location("calibrate_participant", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_configured_paths_uses_sibling_development_file(monkeypatch, tmp_path):
    calibration = tmp_path / "calibration.json"
    monkeypatch.setenv("LAB02_CALIBRATION_FILE", str(calibration))
    monkeypatch.delenv("LAB02_DEVELOPMENT_MEASUREMENTS_FILE", raising=False)

    observed_calibration, observed_measurements = MODULE.configured_paths()

    assert observed_calibration == calibration
    assert observed_measurements == tmp_path / "development-measurements.json"


def test_configured_paths_requires_private_calibration_location(monkeypatch):
    monkeypatch.delenv("LAB02_CALIBRATION_FILE", raising=False)

    with pytest.raises(ValueError, match="Private calibration path"):
        MODULE.configured_paths()


def test_calibration_is_current_requires_matching_context(tmp_path):
    path = tmp_path / "calibration.json"
    payload = calibrate(
        {
            "context": {
                "corpus_id": "contracts-baseline-02-es",
                "region": "us-chicago-1",
                "model_id": "cohere.embed-v4.0",
                "dimension": 1536,
            },
            "rows": [
                {"question_id": "D01", "distance": 0.2, "relevant": True},
                {"question_id": "D01", "distance": 0.8, "relevant": False},
                {"question_id": "D02", "distance": 0.2, "relevant": True},
                {"question_id": "D02", "distance": 0.8, "relevant": False},
                {"question_id": "D03", "distance": 0.2, "relevant": False},
            ],
        }
    )
    path.write_text(json.dumps(payload), encoding="utf-8")

    class Settings:
        region = "us-chicago-1"
        embedding_model_id = "cohere.embed-v4.0"
        vector_dimension = 1536

    assert MODULE.calibration_is_current(path, Settings())
