"""Seed deterministic synthetic procedural guidelines for Lab 1 OCI validation."""

from __future__ import annotations

import os
from getpass import getpass

import oracledb
from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
from oracleagentmemory.core.dbsearch import SearchStrategy


GUIDELINES = {
    "team-a": "Team A guideline: preserve backward compatibility and add contract tests before an API change.",
    "team-b": "Team B guideline: rollout database migration in two controlled phases.",
}
AGENT_ID = "api-agent"


def required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_memory_client() -> OracleAgentMemory:
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
        memory_store_id=required_environment("LAB01_MEMORY_STORE_ID"),
        search_strategy=SearchStrategy.KEYWORD,
        memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
    )


def has_guideline(memory: OracleAgentMemory, team_id: str, content: str) -> bool:
    records = memory.list_memories(user_id=team_id, limit=100)
    return any(record.content == content for record in records)


def main() -> None:
    memory = create_memory_client()
    for team_id, content in GUIDELINES.items():
        if has_guideline(memory, team_id, content):
            print(f"SEED_STATUS {team_id} existing")
            continue
        memory.add_memory(
            content,
            memory_type="guideline",
            user_id=team_id,
            agent_id=AGENT_ID,
            metadata={"team": team_id, "synthetic": True, "lab": "lab01"},
        )
        print(f"SEED_STATUS {team_id} created")


if __name__ == "__main__":
    main()
