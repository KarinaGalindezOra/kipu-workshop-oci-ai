"""Approved administrator: create one Lab 2 participant; never run during student queries."""

import argparse
import os
import string
from getpass import getpass
from pathlib import Path

import oracledb
from dotenv import load_dotenv
from lab02_contract_rag.participant import participant_id


def safe_error_code(error: Exception) -> str:
    detail = error.args[0] if error.args else error
    return str(
        getattr(detail, "full_code", None) or getattr(detail, "code", None) or type(error).__name__
    )


def validate_participant_password(password: str) -> None:
    if not 16 <= len(password) <= 64:
        raise ValueError("New participant password must contain 16-64 characters")
    forbidden = {" ", '"', "'"}
    if any(character not in string.printable or character in forbidden for character in password):
        raise ValueError(
            "New participant password must use printable ASCII without spaces or quotation marks"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant-id", required=True, type=participant_id)
    parser.add_argument("--confirm-create-participant", action="store_true")
    args = parser.parse_args()
    if not args.confirm_create_participant:
        parser.error(
            "Review the SQL, quota and user scope, obtain approval, then acknowledge creation"
        )
    load_dotenv()
    password = getpass("New participant password (16-64 approved characters): ")
    if password != getpass("Confirm new participant password: "):
        raise SystemExit("Passwords differ; no database connection opened")
    try:
        validate_participant_password(password)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    try:
        with (
            oracledb.connect(
                user=os.environ["LAB02_BOOTSTRAP_USERNAME"],
                password=getpass("Approved administrator password: "),
                dsn=os.environ["ADB_CONNECT_STRING"],
                config_dir=os.environ["ADB_WALLET_DIR"],
                wallet_location=os.environ["ADB_WALLET_DIR"],
                wallet_password=getpass("Wallet password: "),
            ) as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(
                Path(__file__).with_name("06_create_lab02_participant.sql").read_text(),
                participant_code=args.participant_id.upper(),
                participant_password=password,
            )
        print("LAB02_PARTICIPANT_SCHEMA_CREATED")
    except oracledb.Error as error:
        raise SystemExit(
            f"Bootstrap failed with database error code {safe_error_code(error)}; "
            "audit privately before retrying"
        ) from None
    except Exception:
        raise SystemExit(
            "Bootstrap failed; administrator must audit privately before retrying"
        ) from None


if __name__ == "__main__":
    main()
