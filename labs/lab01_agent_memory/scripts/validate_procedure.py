"""Validate a participant-authored synthetic procedure without contacting OCI."""

from __future__ import annotations

import argparse
from pathlib import Path

from lab01_agent_memory.procedure_builder import load_procedure_definition


def main() -> None:
    """Parse a JSON procedure and print only safe, design-relevant fields."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("procedure", type=Path, help="Path to a synthetic procedure JSON file")
    args = parser.parse_args()
    procedure = load_procedure_definition(args.procedure)
    print("LAB01_PROCEDURE_VALID True")
    print(f"PROCEDURE_ID {procedure.procedure_id}")
    print(f"VERSION {procedure.version}")
    print(f"DOMAIN {procedure.domain}")
    print(f"TRIGGER_TERMS {','.join(procedure.trigger_terms)}")
    print(f"REQUIRED_EVIDENCE_COUNT {len(procedure.required_evidence)}")


if __name__ == "__main__":
    main()
