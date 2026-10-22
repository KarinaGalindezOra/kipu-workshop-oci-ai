"""Validate bidirectional context isolation for the Lab 1 OCI memory store."""

from __future__ import annotations

import argparse
import os
from getpass import getpass
from pathlib import Path

import oracledb
from lab01_agent_memory.live_evidence import create_live_evidence, write_live_evidence
from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
from oracleagentmemory.core.dbsearch import SearchStrategy

TEAM_A = "team-a"
TEAM_B = "team-b"


def required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_memory_client() -> tuple[OracleAgentMemory, oracledb.ConnectionPool]:
    wallet_dir = required_environment("LAB01_WALLET_DIR")
    pool = oracledb.create_pool(
        user=required_environment("LAB01_DB_USER"),
        password=getpass("Database password: "),
        dsn=required_environment("LAB01_DB_DSN"),
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=getpass("Wallet password: "),
        min=1,
        max=1,
        increment=1,
    )
    return OracleAgentMemory(
        connection=pool,
        schema_policy=SchemaPolicy.REQUIRE_EXISTING,
        schema_owner=required_environment("LAB01_MEMORY_SCHEMA_OWNER"),
        memory_store_id=required_environment("LAB01_MEMORY_STORE_ID"),
        search_strategy=SearchStrategy.KEYWORD,
        memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
    ), pool


def contents_for(memory: OracleAgentMemory, team_id: str) -> list[str]:
    results = memory.search(
        "guideline",
        user_id=team_id,
        exact_user_match=True,
        record_types=["guideline"],
        max_results=10,
    )
    return [result.content for result in results]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-path",
        type=Path,
        help=(
            "Optional safe JSON evidence path. The output contains no credentials "
            "or database identifiers."
        ),
    )
    args = parser.parse_args()
    memory, pool = create_memory_client()
    try:
        team_a_contents = contents_for(memory, TEAM_A)
        team_b_contents = contents_for(memory, TEAM_B)
    finally:
        pool.close()
    team_a_passed = any("Team A guideline" in item for item in team_a_contents) and all(
        "Team B guideline" not in item for item in team_a_contents
    )
    team_b_passed = any("Team B guideline" in item for item in team_b_contents) and all(
        "Team A guideline" not in item for item in team_b_contents
    )
    print("TEAM_A_RESULT_COUNT", len(team_a_contents))
    print("TEAM_A_ISOLATION_PASS", team_a_passed)
    print("TEAM_B_RESULT_COUNT", len(team_b_contents))
    print("TEAM_B_ISOLATION_PASS", team_b_passed)
    if args.output_path:
        evidence = create_live_evidence(
            team_a_result_count=len(team_a_contents),
            team_a_isolation_passed=team_a_passed,
            team_b_result_count=len(team_b_contents),
            team_b_isolation_passed=team_b_passed,
        )
        output_path = write_live_evidence(evidence, args.output_path)
        print("LIVE_EVIDENCE_PATH", output_path)
    if not team_a_passed or not team_b_passed:
        raise SystemExit("Isolation validation failed")


if __name__ == "__main__":
    main()
