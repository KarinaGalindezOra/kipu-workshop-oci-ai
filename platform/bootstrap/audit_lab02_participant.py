"""Read-only audit of one Lab 2 participant schema after a bootstrap attempt."""

import argparse
import json
import os
from getpass import getpass

import oracledb
from dotenv import load_dotenv
from lab02_contract_rag.participant import participant_id, participant_schema


def safe_error_code(error: Exception) -> str:
    detail = error.args[0] if error.args else error
    return str(
        getattr(detail, "full_code", None) or getattr(detail, "code", None) or type(error).__name__
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant-id", required=True, type=participant_id)
    args = parser.parse_args()
    load_dotenv()
    username = participant_schema(args.participant_id)

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
                "SELECT account_status FROM dba_users WHERE username = :username",
                username=username,
            )
            account = cursor.fetchone()
            cursor.execute(
                "SELECT COUNT(*) FROM dba_tables WHERE owner = :username "
                "AND table_name = 'LAB02_CONTRACT_CHUNKS'",
                username=username,
            )
            table_count = int(cursor.fetchone()[0])
            cursor.execute(
                "SELECT privilege FROM dba_sys_privs WHERE grantee = :username ORDER BY privilege",
                username=username,
            )
            privileges = [str(row[0]) for row in cursor]
    except oracledb.Error as error:
        print(json.dumps({"status": "connection_failed", "error_code": safe_error_code(error)}))
        raise SystemExit(2) from None

    print(
        json.dumps(
            {
                "status": "audited",
                "participant_exists": account is not None,
                "account_status": account[0] if account else None,
                "contract_table_exists": table_count == 1,
                "system_privileges": privileges,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
