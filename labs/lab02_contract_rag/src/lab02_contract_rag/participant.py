"""Participant identity, artifact namespaces and database session checks."""

import re
from pathlib import Path
from uuid import uuid4


def participant_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"p(?:00[1-9]|0[1-9][0-9]|[1-9][0-9]{2})", value
    ):
        raise ValueError("Participant ID must be p001 through p999")
    return value


def participant_schema(value: str) -> str:
    return f"KHIPU_L2_{participant_id(value).upper()}"


def artifact_directory(root: Path, value: str, run_id: str | None = None) -> Path:
    """Output directories are organizational; DB permissions provide data isolation."""
    run_id = run_id or str(uuid4())
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Run ID cannot contain path components")
    return root / participant_id(value) / run_id


def assert_peer_access_denied(connection, peer_id: str, table_name: str) -> None:
    """Probe a known-existing peer table. Administrator must attest its existence first."""
    from .live_validation import validated_table_name

    owner = participant_schema(peer_id)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {owner}.{validated_table_name(table_name)} WHERE 1=0"
            )
    except Exception as exc:
        error = exc.args[0] if exc.args else None
        if getattr(error, "code", None) in {942, 1031}:
            return
        raise ValueError("Isolation probe failed for a reason other than access denial") from None
    raise ValueError("Isolation failed: the participant can read a peer table")


def validate_database_session(connection, value: str) -> None:
    expected = participant_schema(value)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT SYS_CONTEXT('USERENV', 'SESSION_USER'), "
            "SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM dual"
        )
        session_user, current_schema = cursor.fetchone()
        if session_user != expected or current_schema != expected:
            raise ValueError("Database session is not the assigned participant schema")
        cursor.execute("SELECT privilege FROM session_privs WHERE privilege LIKE '%ANY%'")
        if cursor.fetchone() is not None:
            raise ValueError("Participant session has excessive cross-schema privileges")
        cursor.execute("SELECT role FROM session_roles WHERE role = 'DBA'")
        if cursor.fetchone() is not None:
            raise ValueError("Administrative roles are forbidden for participants")
