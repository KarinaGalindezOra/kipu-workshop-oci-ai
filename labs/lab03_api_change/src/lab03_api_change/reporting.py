"""Evidence report generation for the Lab 3 controlled API change."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .analysis import ChangeImpact


def write_evidence(output_dir: Path, impacts: list[ChangeImpact]) -> None:
    """Write reviewable JSON and Markdown evidence without modifying source code."""

    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "change_scope": "synthetic Payments API v1 to v2",
        "automation_boundary": "analysis and tests only; no deployment or payment execution",
        "impact_count": len(impacts),
        "impacts": [asdict(impact) for impact in impacts],
        "acceptance_tests": [impact.required_test for impact in impacts],
        "patch_review_required": True,
    }
    (output_dir / "lab03-change-evidence.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Lab 3 API Change Evidence",
        "",
        "Scope: synthetic Payments API v1 to v2",
        "Automation boundary: analysis and tests only; no deployment or payment execution.",
        "",
        "| ID | Severity | Change | Required regression test |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {impact.change_id} | {impact.severity} | {impact.summary} | {impact.required_test} |"
        for impact in impacts
    )
    lines.extend(["", "Patch review required: true", ""])
    (output_dir / "lab03-change-evidence.md").write_text("\n".join(lines), encoding="utf-8")
