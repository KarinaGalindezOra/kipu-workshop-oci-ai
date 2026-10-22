"""Run the offline Lab 1 scope and token-comparison demonstration."""

import argparse
import json
from pathlib import Path

from .metrics import compare_prompt_usage
from .models import MemoryScope
from .reporting import write_evidence_artifacts
from .scenario import GUIDELINES, baseline_prompt, compact_prompt
from .store import ScopedMemoryStore

DEFAULT_QUESTION = "How should we process a repeated payment request for the API contract v2?"


def build_report(team_id: str, question: str = DEFAULT_QUESTION) -> dict[str, object]:
    """Build the deterministic report used in the participant walkthrough."""

    if not question or question.strip() != question:
        raise ValueError("question must be a non-empty trimmed string")

    store = ScopedMemoryStore()
    team_scope = MemoryScope(team_id=team_id, agent_id="khipu-workshop-agent", thread_id="lab01")
    other_team_id = "team-02" if team_id != "team-02" else "team-01"
    other_scope = MemoryScope(
        team_id=other_team_id,
        agent_id="khipu-workshop-agent",
        thread_id="lab01",
    )
    for guideline in GUIDELINES:
        store.add_guideline(team_scope, guideline)

    matches = store.search(team_scope, "payment idempotency contract version")
    other_team_matches = store.search(other_scope, "payment idempotency contract version")
    comparison = compare_prompt_usage(
        baseline_prompt(question),
        compact_prompt(question),
        [match.content for match in matches],
    )

    return {
        "team_id": team_id,
        "query": question,
        "retrieved_guidelines": [match.identifier for match in matches],
        "other_team_retrieved_guidelines": [match.identifier for match in other_team_matches],
        "isolation_passed": not other_team_matches,
        "token_measurement_type": "deterministic_estimate_not_provider_billing_usage",
        "prompt_comparison": comparison.as_dict(),
    }


def main() -> None:
    """Print a JSON report that can be captured as workshop evidence."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-id", default="team-01", help="Unique workshop team identifier")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional directory where JSON, Markdown, and SVG evidence artifacts are written",
    )
    args = parser.parse_args()
    report = build_report(args.team_id)
    if args.output_dir:
        paths = write_evidence_artifacts(report, args.output_dir)
        report["evidence_artifacts"] = {name: str(path) for name, path in paths.items()}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
