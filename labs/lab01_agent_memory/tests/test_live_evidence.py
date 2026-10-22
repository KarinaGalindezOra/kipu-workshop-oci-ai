import pytest
from lab01_agent_memory.live_evidence import create_live_evidence, load_live_evidence


def test_live_evidence_is_portable_and_safe() -> None:
    evidence = create_live_evidence(
        team_a_result_count=1,
        team_a_isolation_passed=True,
        team_b_result_count=1,
        team_b_isolation_passed=True,
    )

    assert evidence["contains_no_secrets"] is True
    assert evidence["teams"]["team-a"]["result_count"] == 1
    assert evidence["teams"]["team-b"]["isolation_passed"] is True


def test_live_evidence_rejects_secret_unmarked_payload() -> None:
    with pytest.raises(ValueError, match="contains no secrets"):
        load_live_evidence(
            '{"schema_version":"1.0","evidence_type":"lab01_oci_isolation_validation",'
            '"generated_at_utc":"2026-10-13T00:00:00+00:00","contains_no_secrets":false,'
            '"teams":{"team-a":{"result_count":1,"isolation_passed":true},'
            '"team-b":{"result_count":1,"isolation_passed":true}}}'
        )
