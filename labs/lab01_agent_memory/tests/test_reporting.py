from pathlib import Path

from lab01_agent_memory.demo import build_report
from lab01_agent_memory.reporting import (
    render_evidence_markdown,
    render_token_comparison_svg,
    write_evidence_artifacts,
)


def test_svg_distinguishes_compact_prompt_from_retrieved_memory() -> None:
    chart = render_token_comparison_svg(build_report("team-01"))

    assert "Baseline prompt" in chart
    assert "Compact prompt plus retrieved memory" in chart
    assert "Repeated procedural tokens removed from the base prompt" in chart


def test_markdown_records_isolation_and_estimate_disclaimer() -> None:
    summary = render_evidence_markdown(build_report("team-01"))

    assert "Isolation passed: `True`" in summary
    assert "not OCI billing usage" in summary
    assert "Estimated request-input reduction after retrieval" in summary


def test_evidence_artifacts_are_written(tmp_path: Path) -> None:
    paths = write_evidence_artifacts(build_report("team-01"), tmp_path)

    assert paths["report"].is_file()
    assert paths["summary"].is_file()
    assert paths["chart"].is_file()
    assert "<svg" in paths["chart"].read_text(encoding="utf-8")
