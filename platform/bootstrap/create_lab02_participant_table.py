"""Create the Lab 2 vector table once in one approved participant schema."""

import argparse
import os
from getpass import getpass

import oracledb
from dotenv import load_dotenv
from lab02_contract_rag.participant import (
    participant_id,
    participant_schema,
    validate_database_session,
)

TABLE_NAME = "LAB02_CONTRACT_CHUNKS"


def positive_dimension(value: str) -> int:
    dimension = int(value)
    if dimension <= 0 or dimension > 4096:
        raise argparse.ArgumentTypeError("Vector dimension must be between 1 and 4096")
    return dimension


def table_statements(vector_dimension: int) -> tuple[str, str]:
    if vector_dimension <= 0:
        raise ValueError("Vector dimension must be positive")
    return (
        f"""
        CREATE TABLE lab02_contract_chunks (
            chunk_id VARCHAR2(128) PRIMARY KEY,
            corpus_id VARCHAR2(128) NOT NULL,
            api_name VARCHAR2(64) NOT NULL,
            contract_version VARCHAR2(8) NOT NULL,
            data_classification VARCHAR2(32) NOT NULL,
            content_hash VARCHAR2(64) NOT NULL,
            embedding_model_id VARCHAR2(512) NOT NULL,
            embedding_dimension NUMBER NOT NULL,
            embedding_input_hash VARCHAR2(64) NOT NULL,
            metadata_json CLOB NOT NULL CHECK (metadata_json IS JSON),
            embedding VECTOR({vector_dimension}, FLOAT32) NOT NULL,
            loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
            CHECK (contract_version IN ('v1', 'v2')),
            CHECK (data_classification = 'synthetic')
        )
        """,
        """
        CREATE INDEX lab02_contract_scope_ix
            ON lab02_contract_chunks (corpus_id, api_name, contract_version)
        """,
    )


def table_exists(cursor) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM user_tables WHERE table_name = :table_name",
        table_name=TABLE_NAME,
    )
    return int(cursor.fetchone()[0]) > 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant-id", required=True, type=participant_id)
    parser.add_argument("--vector-dimension", type=positive_dimension, default=1536)
    parser.add_argument("--confirm-create-table", action="store_true")
    args = parser.parse_args()
    if not args.confirm_create_table:
        parser.error("Obtain approval and acknowledge participant table creation")

    load_dotenv()
    expected_user = participant_schema(args.participant_id)
    supplied_user = os.getenv("ADB_USERNAME", expected_user).upper()
    if supplied_user != expected_user:
        raise SystemExit("ADB_USERNAME must be the assigned participant schema")

    participant_password = getpass("Participant schema password: ")
    wallet_password = getpass("Wallet password: ")
    try:
        with (
            oracledb.connect(
                user=expected_user,
                password=participant_password,
                dsn=os.environ["ADB_CONNECT_STRING"],
                config_dir=os.environ["ADB_WALLET_DIR"],
                wallet_location=os.environ["ADB_WALLET_DIR"],
                wallet_password=wallet_password,
            ) as connection,
            connection.cursor() as cursor,
        ):
            validate_database_session(connection, args.participant_id)
            if table_exists(cursor):
                raise SystemExit("Participant table already exists; audit before reuse")
            create_table, create_index = table_statements(args.vector_dimension)
            cursor.execute(create_table)
            cursor.execute(create_index)
        print("LAB02_PARTICIPANT_TABLE_CREATED")
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(
            "Table bootstrap failed; administrator must audit privately before retrying"
        ) from None


if __name__ == "__main__":
    main()
