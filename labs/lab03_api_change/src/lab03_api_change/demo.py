"""Run the deterministic analysis gate for Lab 3."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyze_api_change
from .reporting import write_evidence


def main() -> None:
    """Generate a bounded API-change report for facilitator review."""

    parser = argparse.ArgumentParser(description="Run the Lab 3 API-change analysis demo.")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/lab03/team-01"))
    args = parser.parse_args()

    impacts = analyze_api_change()
    write_evidence(args.output_dir, impacts)
    impact_ids = {impact.change_id for impact in impacts}
    print(f"ANALYSIS_CHANGE_COUNT {len(impacts)}")
    print(f"REQUIRED_IMPACTS_PRESENT {impact_ids == {'PAY-001', 'PAY-002', 'PAY-003'}}")
    print("PATCH_REVIEW_REQUIRED True")
    print("REGRESSION_TESTS_REQUIRED True")


if __name__ == "__main__":
    main()
