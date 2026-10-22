"""Generate participant-facing evidence for the offline Lab 1 demonstration."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _token_rows(prompt_comparison: dict[str, int]) -> list[tuple[str, int, str]]:
    """Return ordered, participant-friendly values for the token comparison."""

    return [
        (
            "Baseline prompt",
            prompt_comparison["baseline_prompt_tokens"],
            "All procedural rules are repeated in every request.",
        ),
        (
            "Compact prompt",
            prompt_comparison["memory_prompt_tokens"],
            "The request refers to scoped memory instead of repeating all rules.",
        ),
        (
            "Compact prompt plus retrieved memory",
            prompt_comparison["estimated_request_tokens_with_memory"],
            "Only guidelines relevant to this request are added as context.",
        ),
    ]


def render_token_comparison_svg(report: dict[str, Any]) -> str:
    """Render a dependency-free SVG token comparison for workshop evidence."""

    comparison = report["prompt_comparison"]
    rows = _token_rows(comparison)
    max_tokens = max(value for _, value, _ in rows) or 1
    chart_width = 480
    bar_x = 330
    bar_height = 38
    row_height = 84
    colors = ("#C74634", "#4A6FA5", "#2F855A")
    bars: list[str] = []
    for index, ((label, value, explanation), color) in enumerate(zip(rows, colors, strict=True)):
        y = 104 + index * row_height
        width = round(chart_width * value / max_tokens)
        bars.extend(
            (
                f'<text x="36" y="{y + 16}" class="label">{html.escape(label)}</text>',
                f'<text x="36" y="{y + 37}" class="detail">{html.escape(explanation)}</text>',
                f'<rect x="{bar_x}" y="{y}" width="{width}" height="{bar_height}" rx="6" fill="{color}"/>',
                f'<text x="{bar_x + width + 12}" y="{y + 25}" class="value">{value} tokens</text>',
            )
        )

    avoided = comparison["repeated_prompt_reduction_tokens"]
    request_reduction = comparison["estimated_request_reduction_tokens"]
    team_id = html.escape(str(report["team_id"]))
    return "\n".join(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="426" viewBox="0 0 900 426" role="img" aria-labelledby="title desc">',
            '<title id="title">Lab 1 token comparison</title>',
            '<desc id="desc">Comparison between repeated procedural prompts and scoped memory retrieval.</desc>',
            '<style>.title{font:700 22px Arial,sans-serif;fill:#1f2937}.subtitle{font:14px Arial,sans-serif;fill:#4b5563}.label{font:700 14px Arial,sans-serif;fill:#111827}.detail{font:12px Arial,sans-serif;fill:#4b5563}.value{font:700 14px Arial,sans-serif;fill:#111827}.callout{font:700 16px Arial,sans-serif;fill:#166534}</style>',
            '<rect width="900" height="426" fill="#ffffff"/>',
            '<text x="36" y="42" class="title">Lab 1: procedural memory and input-token comparison</text>',
            f'<text x="36" y="68" class="subtitle">Team scope: {team_id}. Values are deterministic estimates, not OCI billing usage.</text>',
            *bars,
            '<rect x="36" y="352" width="828" height="56" rx="6" fill="#DCFCE7"/>',
            f'<text x="52" y="374" class="callout">Repeated procedural tokens removed from the base prompt: {avoided}</text>',
            f'<text x="52" y="396" class="subtitle">Estimated request-input reduction after relevant memory is retrieved: {request_reduction} tokens</text>',
            '</svg>',
        )
    )


def render_evidence_markdown(report: dict[str, Any]) -> str:
    """Create a concise evidence record that facilitators can review with teams."""

    comparison = report["prompt_comparison"]
    retrieved = ", ".join(report["retrieved_guidelines"]) or "None"
    cross_team = ", ".join(report["other_team_retrieved_guidelines"]) or "None"
    return "\n".join(
        (
            "# Lab 1 evidence record",
            "",
            f"- Team scope: `{report['team_id']}`",
            f"- Isolation passed: `{report['isolation_passed']}`",
            f"- Retrieved guidelines: {retrieved}",
            f"- Cross-team retrieval: {cross_team}",
            "",
            "| Measurement | Tokens |",
            "| --- | ---: |",
            f"| Baseline prompt | {comparison['baseline_prompt_tokens']} |",
            f"| Compact prompt | {comparison['memory_prompt_tokens']} |",
            f"| Retrieved guidelines | {comparison['retrieved_guideline_tokens']} |",
            f"| Compact prompt plus retrieved memory | {comparison['estimated_request_tokens_with_memory']} |",
            f"| Repeated prompt tokens avoided | {comparison['repeated_prompt_reduction_tokens']} |",
            f"| Estimated request-input reduction after retrieval | {comparison['estimated_request_reduction_tokens']} |",
            "",
            "The values are deterministic token estimates for workshop comparison. They are not OCI billing usage and do not include memory extraction, embedding, or retrieval lifecycle tokens.",
            "",
        )
    )


def write_evidence_artifacts(report: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    """Write JSON, Markdown, and SVG artifacts for a single team demonstration."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "report": output_dir / "lab01-evidence.json",
        "summary": output_dir / "lab01-evidence.md",
        "chart": output_dir / "lab01-token-comparison.svg",
    }
    paths["report"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    paths["summary"].write_text(render_evidence_markdown(report), encoding="utf-8")
    paths["chart"].write_text(render_token_comparison_svg(report), encoding="utf-8")
    return paths
