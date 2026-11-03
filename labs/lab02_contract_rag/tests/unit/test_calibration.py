import pytest
from lab02_contract_rag.calibration import calibrate


def measurements():
    return {
        "context": {
            "corpus_id": "contracts-baseline-01",
            "model_id": "model",
            "region": "us-ashburn-1",
            "dimension": 2,
        },
        "rows": [
            {"question_id": "D01", "relevant": True, "distance": 0.2},
            {"question_id": "D02", "relevant": True, "distance": 0.3},
            {"question_id": "D03", "relevant": False, "distance": 0.7},
        ],
    }


def test_threshold_preserves_positive_candidate_recall():
    result = calibrate(measurements())

    assert result["max_cosine_distance"] == 0.32
    assert result["negative_overlap_detected"] is False
    assert result["evidence_selection_required"] is True


def test_overlapping_negatives_are_recorded_not_mistaken_for_evidence():
    data = measurements()
    data["rows"][-1]["distance"] = 0.1
    result = calibrate(data)

    assert result["max_cosine_distance"] == 0.32
    assert result["negative_overlap_detected"] is True
    assert result["evidence_selection_required"] is True


def test_acceptance_set_cannot_be_used_to_calibrate():
    data = measurements()
    data["rows"][-1]["question_id"] = "T01"
    with pytest.raises(ValueError, match="development"):
        calibrate(data)
