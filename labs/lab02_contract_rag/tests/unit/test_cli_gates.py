import json
import sys
from dataclasses import replace
from unittest.mock import Mock

import pytest
from lab02_contract_rag import live_validation
from lab02_contract_rag.calibration import calibrate, validate_calibration
from lab02_contract_rag.corpus import load_corpus


def test_paid_runner_requires_consent_before_client_or_database(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["runner", "--question", "In v2, what endpoint?"])
    forbidden = Mock(side_effect=AssertionError("Network must not be reached"))
    monkeypatch.setattr(live_validation, "create_inference_client", forbidden)
    monkeypatch.setattr(live_validation, "create_database_connection", forbidden)
    with pytest.raises(SystemExit) as error:
        live_validation.main()
    assert error.value.code == 2
    forbidden.assert_not_called()


@pytest.mark.parametrize("question", ["How do I update status?"])
def test_clarification_and_unknown_topics_do_not_require_live_calls(
    monkeypatch, tmp_path, question
):
    monkeypatch.setattr(
        sys, "argv", ["runner", "--question", question, "--output-dir", str(tmp_path)]
    )
    monkeypatch.setenv("LAB02_PARTICIPANT_ID", "p001")
    forbidden = Mock(side_effect=AssertionError("Network must not be reached"))
    monkeypatch.setattr(live_validation, "create_inference_client", forbidden)
    live_validation.main()
    forbidden.assert_not_called()
    payload = json.loads(next(tmp_path.glob("p001/*/lab02-evidence.json")).read_text())
    assert payload["status"] in {"needs_clarification", "insufficient_evidence"}


def test_mutated_citation_metadata_is_rejected_by_oci_retriever():
    from dataclasses import asdict

    from lab02_contract_rag.live_validation import LiveLab02Settings, retrieve_evidence

    settings = LiveLab02Settings(
        "placeholder",
        "model",
        "chat",
        "TEAM",
        "dsn",
        "wallet",
        2,
        "CHUNKS",
        3,
        "DEFAULT",
        None,
        max_cosine_distance=0.4,
    )
    chunk = next(c for c in load_corpus() if c.contract_version == "v2")
    chunk = replace(
        chunk, source_uri="synthetic://forged.md", embedding_model_id="model", embedding_dimension=2
    )
    cursor = Mock()
    cursor.__iter__ = Mock(return_value=iter([(json.dumps(asdict(chunk)), 0.2)]))
    with pytest.raises(ValueError, match="manifest"):
        retrieve_evidence(cursor, "CHUNKS", "v2", [1, 2], 3, settings)


def test_calibration_rejects_changed_embedding_context(tmp_path):
    payload = calibrate(
        {
            "context": {
                "corpus_id": "contracts-baseline-02-es",
                "region": "region",
                "model_id": "model",
                "dimension": 2,
            },
            "rows": [
                {"question_id": "D01", "relevant": True, "distance": 0.1},
                {"question_id": "D02", "relevant": True, "distance": 0.2},
                {"question_id": "D03", "relevant": False, "distance": 0.9},
            ],
        }
    )
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps(payload))
    assert validate_calibration(path, region="region", model_id="model", dimension=2) == 0.22
    with pytest.raises(ValueError, match="context"):
        validate_calibration(path, region="other", model_id="model", dimension=2)
