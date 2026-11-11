"""Participant-only commands for an already provisioned assignment. No inference calls."""

from __future__ import annotations

import argparse
import json
import re
from contextlib import contextmanager
from getpass import getpass
from pathlib import Path
from uuid import uuid4

from .domain import Request
from .live import LiveBackend, Settings, read_lob
from .oci_profile import profile_user

REPOSITORY = Path(__file__).resolve().parents[4]


class ParticipantInputError(ValueError):
    """Safe, author-written participant guidance without raw driver details."""


def private_output(path: Path) -> Path:
    target = path.expanduser().resolve()
    if target.is_relative_to(REPOSITORY) or target.exists():
        raise ParticipantInputError("Choose a new private output file outside the repository")
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def validate_exercise_sql(source: str) -> str:
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("--"))
    code = code.strip().removesuffix("/").strip()
    if "TODO" in source.upper() or "-20010" in code:
        raise ParticipantInputError("Complete all exercise TODOs before installing the function")
    if not re.match(r"(?is)^CREATE\s+OR\s+REPLACE\s+FUNCTION\s+FIND_RELATED_REQUESTS\s*\(", code):
        raise ParticipantInputError(
            "Only the FIND_RELATED_REQUESTS exercise function can be installed"
        )
    if len(re.findall(r"(?i)\bCREATE\b", code)) != 1 or not re.search(r"(?is)END;\s*$", code):
        raise ParticipantInputError("Provide exactly one complete function, not a SQL script")
    if re.search(
        r"(?i)\b(?:ALTER|DROP|GRANT|REVOKE|TRUNCATE|INSERT|UPDATE|DELETE|MERGE|COMMIT|ROLLBACK)\b|EXECUTE\s+IMMEDIATE|UTL_HTTP|DBMS_CLOUD",
        code,
    ):
        raise ParticipantInputError("The exercise must use a fixed read-only query")
    if not re.search(r"(?i)\bAUTHID\s+CURRENT_USER\b", code):
        raise ParticipantInputError("Preserve AUTHID CURRENT_USER in the exercise")
    return code


def validate_role(source: str) -> str:
    text = source.strip()
    if not text or len(text) > 4000 or "TODO" in text.upper():
        raise ParticipantInputError(
            "Complete the role exercise with 1 to 4000 characters and no TODOs"
        )
    return text


@contextmanager
def connected(settings: Settings, *, repair_exercise: bool = False):
    import oci

    config = oci.config.from_file(profile_name=settings.profile)
    if (
        config["tenancy"] != settings.expected_tenancy
        or profile_user(config) != settings.expected_user
    ):
        raise ParticipantInputError("OCI profile does not match the private assignment")
    backend = LiveBackend(settings, getpass("Database password: "), getpass("Wallet password: "))
    try:
        if repair_exercise:
            with backend.connection.cursor() as cur:
                for sql in (
                    "select count(*) from WS3_ACTIVE",
                    "select count(*) from USER_AI_AGENT_TEAM_HISTORY where state='RUNNING'",
                ):
                    cur.execute(sql)
                    if cur.fetchone()[0]:
                        raise ParticipantInputError(
                            "An investigation is active; do not replace its tool"
                        )
        else:
            backend.readiness(require_team=False)
        yield backend
    finally:
        backend.close()


def direct_tool_test(backend, payment_id: str) -> dict:
    Request("Direct exercise test", payment_id, "v2").validate()
    run_id = str(uuid4())
    with backend.connection.cursor() as cur:
        cur.execute(
            "insert into WS3_ACTIVE(slot,run_id,payment_id) values(1,:r,:p)", r=run_id, p=payment_id
        )
    backend.connection.commit()
    try:
        import oracledb

        with backend.connection.cursor() as cur:
            raw = cur.callfunc("FIND_RELATED_REQUESTS", oracledb.DB_TYPE_CLOB, [payment_id])
            value = json.loads(read_lob(raw))
            requests = value.get("requests")
            if not isinstance(requests, list) or any(
                not isinstance(row, dict)
                or set(row) != {"request_id", "idempotency_key", "payload_hash"}
                or any(not isinstance(v, str) or not v for v in row.values())
                for row in requests
            ):
                raise ParticipantInputError(
                    "Tool output does not match the required requests schema"
                )
            cur.execute(
                "select request_id,idempotency_key,payload_hash from WS3_REQUESTS where payment_id=:p order by request_id",
                p=payment_id,
            )
            expected = [
                {"request_id": r, "idempotency_key": k, "payload_hash": h}
                for r, k, h in cur.fetchall()
            ]
            if requests != expected:
                raise ParticipantInputError(
                    "Tool results differ from the assigned payment's stored requests"
                )
            cur.execute(
                "select count(*) from WS3_TOOL_LOG where run_id=:r and tool_name='find_related_requests' and payment_id=:p",
                r=run_id,
                p=payment_id,
            )
            if cur.fetchone()[0] != 1:
                raise ParticipantInputError("Expected one independent observation from WS3_TRACE")
        return {
            "execution_mode": "direct_database_tool_test",
            "agent_executed": False,
            "inference_calls": 0,
            "payment_id": payment_id,
            "run_id": run_id,
            "result": value,
        }
    finally:
        with backend.connection.cursor() as cur:
            cur.execute("delete from WS3_ACTIVE where run_id=:r", r=run_id)
        backend.connection.commit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation",
        choices=[
            "readiness",
            "recover-memory",
            "backup-tool",
            "install-tool",
            "test-tool",
            "backup-agent-role",
            "set-agent-role",
        ],
    )
    parser.add_argument("--session-file", type=Path, required=True)
    parser.add_argument("--sql-file", type=Path)
    parser.add_argument("--role-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--payment-id", default="PAY-104")
    args = parser.parse_args()
    sql = role = target = None
    if args.operation == "install-tool":
        if not args.sql_file:
            parser.error("install-tool requires --sql-file")
        sql = validate_exercise_sql(args.sql_file.read_text(encoding="utf-8-sig"))
    if args.operation == "set-agent-role":
        if not args.role_file:
            parser.error("set-agent-role requires --role-file")
        role = validate_role(args.role_file.read_text(encoding="utf-8-sig"))
    if args.operation in {"backup-tool", "backup-agent-role", "test-tool"}:
        if not args.output:
            parser.error("This operation requires a new private --output file")
        target = private_output(args.output)
    if args.operation == "test-tool":
        Request("Direct exercise test", args.payment_id, "v2").validate()
    settings = Settings.load(args.session_file)
    with connected(settings, repair_exercise=args.operation == "install-tool") as backend:
        if args.operation == "readiness":
            print("ASSIGNMENT_AND_DATABASE_READY; NO_INFERENCE_CALLS")
        elif args.operation == "recover-memory":
            records = backend.memories("payment idempotency")
            print(json.dumps([r.__dict__ for r in records], indent=2))
        elif args.operation == "test-tool":
            result = direct_tool_test(backend, args.payment_id)
            target.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(json.dumps(result, indent=2))
        else:
            with backend.connection.cursor() as cur:
                if args.operation == "backup-tool":
                    cur.execute(
                        "select text from user_source where name='FIND_RELATED_REQUESTS' and type='FUNCTION' order by line"
                    )
                    rows = cur.fetchall()
                    if not rows:
                        raise ParticipantInputError("Assigned exercise function is missing")
                    target.write_text(
                        "CREATE OR REPLACE " + "".join(r[0] for r in rows) + "\n/\n",
                        encoding="utf-8",
                    )
                    print("PRIVATE_TOOL_BACKUP_SAVED")
                elif args.operation == "install-tool":
                    cur.execute(sql)
                    cur.execute(
                        "select line,position from user_errors where name='FIND_RELATED_REQUESTS' and type='FUNCTION' and attribute='ERROR'"
                    )
                    errors = cur.fetchall()
                    if errors:
                        print("COMPILATION_ERROR_LOCATIONS", errors)
                        raise ParticipantInputError(
                            "Exercise compilation failed; correct the file before investigating"
                        )
                    print("ASSIGNED_EXERCISE_FUNCTION_INSTALLED; NO_INFERENCE_CALLS")
                elif args.operation == "backup-agent-role":
                    cur.execute(
                        "select attribute_value from USER_AI_AGENT_ATTRIBUTES where agent_name='WS3_AGENT' and lower(attribute_name)='role'"
                    )
                    row = cur.fetchone()
                    if not row:
                        raise ParticipantInputError("Assigned agent role is missing")
                    target.write_text(read_lob(row[0]), encoding="utf-8")
                    print("PRIVATE_AGENT_ROLE_BACKUP_SAVED")
                elif args.operation == "set-agent-role":
                    cur.execute(
                        "begin DBMS_CLOUD_AI_AGENT.SET_ATTRIBUTE(object_name=>'WS3_AGENT',object_type=>'agent',attribute_name=>'role',attribute_value=>:v); end;",
                        v=role,
                    )
                    backend.connection.commit()
                    cur.execute(
                        "select attribute_value from USER_AI_AGENT_ATTRIBUTES where agent_name='WS3_AGENT' and lower(attribute_name)='role'"
                    )
                    if read_lob(cur.fetchone()[0]) != role:
                        raise ParticipantInputError("Agent role update was not verified")
                    print("ASSIGNED_AGENT_ROLE_UPDATED_AND_VERIFIED; NO_INFERENCE_CALLS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if isinstance(exc, ParticipantInputError):
            print(str(exc))
        code = getattr(exc.args[0], "code", None) if exc.args else None
        print(
            "OPERATION_FAILED",
            type(exc).__name__,
            "database_code=",
            code if isinstance(code, int) else None,
        )
        raise SystemExit(
            "Check the participant troubleshooting guide. Do not share credentials or raw driver errors."
        ) from None
