from lab01_agent_memory.demo import build_report


def test_demo_reports_scope_isolation_and_token_comparison() -> None:
    report = build_report("team-01")

    assert report["isolation_passed"] is True
    assert report["retrieved_guidelines"]
    assert report["other_team_retrieved_guidelines"] == []
    assert report["prompt_comparison"]["repeated_prompt_reduction_tokens"] > 0


def test_demo_keeps_team_two_isolated_from_team_one() -> None:
    report = build_report("team-02")

    assert report["isolation_passed"] is True
    assert report["other_team_retrieved_guidelines"] == []
