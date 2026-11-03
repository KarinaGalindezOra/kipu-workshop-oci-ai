"""Tests for the deterministic API-change analysis."""

from lab03_api_change.analysis import analyze_api_change, impacts_as_dicts


def test_analysis_identifies_all_approved_impacts() -> None:
    impacts = analyze_api_change()

    assert [impact.change_id for impact in impacts] == ["PAY-001", "PAY-002", "PAY-003"]
    assert impacts[0].severity == "high"
    assert "paymentStatus" in impacts[0].summary
    assert "idempotencyKey" in impacts[1].summary


def test_analysis_is_json_compatible() -> None:
    impacts = impacts_as_dicts()

    assert impacts[2]["required_test"].startswith("A valid v2 request returns 202")
