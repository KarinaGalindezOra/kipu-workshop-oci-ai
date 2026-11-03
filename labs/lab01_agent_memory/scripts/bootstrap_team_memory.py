"""Initialize one team-owned Agent Memory store and its synthetic control memory."""

from __future__ import annotations

import argparse
import os
from getpass import getpass
from typing import Any

import oracledb
from lab01_agent_memory.sdk_exercise import AGENT_ID, build_team_scopes
from oracleagentmemory.core import MemoryExtractionConfig, OracleAgentMemory, SchemaPolicy
from oracleagentmemory.core._db.connection import _DBConnectionManager
from oracleagentmemory.core._oraclememorystoreadmin import _OracleAgentMemoryAdmin
from oracleagentmemory.core.dbsearch import SearchStrategy

CONTROL_MEMORY = (
    "Controlled database migrations use two approved phases, evidence checkpoints, "
    "and an explicit rollback decision."
)


def required_environment(name: str) -> str:
    """Read one required non-secret owner connection setting."""

    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def memory_owner_db_user() -> str:
    """Resolve the owner user while keeping the participant session contract simple."""

    return os.environ.get("LAB01_MEMORY_OWNER_DB_USER") or required_environment(
        "LAB01_MEMORY_SCHEMA_OWNER"
    )


def create_owner_pool() -> Any:
    """Open an mTLS pool as the memory schema owner."""

    wallet_dir = required_environment("LAB01_WALLET_DIR")
    pool = oracledb.create_pool(
        user=memory_owner_db_user(),
        password=getpass("Memory owner database password: "),
        dsn=required_environment("LAB01_DB_DSN"),
        config_dir=wallet_dir,
        wallet_location=wallet_dir,
        wallet_password=getpass("Wallet password: "),
        min=1,
        max=1,
        increment=1,
    )
    return pool


def provision_memory_package(pool: Any) -> None:
    """Install the official Agent Memory owner package through the mTLS pool."""

    package_info = _OracleAgentMemoryAdmin(_DBConnectionManager(pool)).install_plsql_package()
    print("PLSQL_PACKAGE_READY", package_info["package_version"])


def create_owner_memory(pool: Any) -> OracleAgentMemory:
    """Open the owner-managed logical store after package provisioning.

    ``LAB01_MEMORY_STORE_ID`` is the SDK logical store name
    (``MEMORY_STORE_NAME`` in ADB), not the internal ``MEMORY_STORE_UID``.
    """

    return OracleAgentMemory(
        connection=pool,
        schema_policy=SchemaPolicy.CREATE_IF_NECESSARY,
        memory_store_id=required_environment("LAB01_MEMORY_STORE_ID"),
        search_strategy=SearchStrategy.KEYWORD,
        memory_extraction_config=MemoryExtractionConfig(extract_memories=False),
    )


def parse_args() -> argparse.Namespace:
    """Parse a stable team code for the one-time bootstrap action."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-code", required=True, help="Assigned team code, for example T01")
    return parser.parse_args()


def main() -> None:
    """Create the store when empty and seed a separate synthetic control scope."""

    args = parse_args()
    scopes = build_team_scopes(args.team_code, "bootstrap")
    confirmation = input(
        "Type BOOTSTRAP after confirming this is the approved team ADB and memory store: "
    ).strip()
    if confirmation != "BOOTSTRAP":
        raise SystemExit("Bootstrap cancelled. No database objects were changed.")

    pool = create_owner_pool()
    try:
        provision_memory_package(pool)
        memory = create_owner_memory(pool)
        existing = memory.list_memories(user_id=scopes.control, limit=100)
        if any(record.content == CONTROL_MEMORY for record in existing):
            print("CONTROL_MEMORY existing")
        else:
            memory.add_memory(
                CONTROL_MEMORY,
                memory_type="guideline",
                user_id=scopes.control,
                agent_id=AGENT_ID,
                metadata={"team_code": args.team_code, "synthetic": "true", "lab": "lab01"},
            )
            print("CONTROL_MEMORY created")
    finally:
        pool.close()
    print("LAB01_TEAM_MEMORY_READY")


if __name__ == "__main__":
    main()
