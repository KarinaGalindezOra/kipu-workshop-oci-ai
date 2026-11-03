"""Create the disposable Lab 1 Oracle AI Agent Memory store when it is empty."""

from __future__ import annotations

import os
from getpass import getpass

import oracledb
from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
from oracleagentmemory.core.dbsearch import SearchStrategy


def required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def create_memory_store() -> OracleAgentMemory:
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
        schema_policy=SchemaPolicy.CREATE_IF_NECESSARY,
        memory_store_id=required_environment("LAB01_MEMORY_STORE_ID"),
        search_strategy=SearchStrategy.KEYWORD,
        memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
    )


def main() -> None:
    store_id = required_environment("LAB01_MEMORY_STORE_ID")
    confirmation = input(
        f"Type CREATE to initialize the empty Lab 1 memory store {store_id}: "
    ).strip()
    if confirmation != "CREATE":
        raise SystemExit("Initialization cancelled. No database objects were changed.")

    create_memory_store()
    print("MEMORY_STORE_READY", store_id)


if __name__ == "__main__":
    main()
