"""Verify existing human confirmations and idempotent no-ops without model calls."""

import argparse
import json
from dataclasses import asdict
from getpass import getpass
from pathlib import Path
from uuid import UUID

from .confirmation import memory_proposal, review
from .domain import Request, digest
from .live import LiveBackend, Settings
from .participant import private_output
from .retained_response import recover


class ReadOnlyCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        self.cursor.__enter__()
        return self

    def __exit__(self, *args):
        return self.cursor.__exit__(*args)

    def execute(self, sql, **bindings):
        normalized = " ".join(sql.upper().split())
        if not normalized.startswith("SELECT ") or "FOR UPDATE" in normalized:
            raise ValueError("Audit stopped before a write or locking operation")
        return self.cursor.execute(sql, **bindings)

    def fetchone(self):
        return self.cursor.fetchone()


class ReadOnlyConnection:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        return ReadOnlyCursor(self.connection.cursor())

    def commit(self):
        raise ValueError("Audit cannot commit writes")

    def rollback(self):
        raise ValueError("Audit stopped before a transaction change")


def replay_saved(backend, key, kind, payload):
    """Exercise the real put_once early return; block all other branches before writes."""
    connection = backend.connection
    backend.connection = ReadOnlyConnection(connection)
    try:
        receipt = backend.put_once(key, kind, payload)
    finally:
        backend.connection = connection
    if receipt != {"write_key": key, "status": "already_saved"}:
        raise ValueError("Expected an existing completed confirmation")
    return receipt


def audit(backend, evidence_root, source_run):
    run = str(UUID(source_run))
    root = Path(evidence_root).expanduser().resolve() / backend.identity / run
    # Require a separately recovered real final answer; never reinterpret a local test.
    retained_path = root / "evidence.revalidated.json"
    if not retained_path.exists():
        retained_path = root / "evidence.json"
    retained = json.loads(retained_path.read_text())
    proposal = retained.get("proposal") or {}
    if retained.get("status") != "answered" or retained.get("execution_mode") not in {
        "live",
        "stored_oci_revalidation",
    }:
        raise ValueError("A validated retained live response is required")
    request = Request(
        "Investigate payment idempotency and prepare a recommendation.",
        proposal["payment_id"],
        proposal["version"],
    )
    result = recover(backend, request, Path(evidence_root), run)
    payloads = {"case": result.proposal, "memory": memory_proposal(result)}
    confirmations = {}
    for kind, payload in payloads.items():
        prior = json.loads((root / (kind + "_confirmation.json")).read_text())
        key = digest(asdict(review(backend.identity, kind, payload)))
        if prior.get("write_key") != key or prior.get("status") not in {"saved", "already_saved"}:
            raise ValueError("Require the original human confirmation of this exact content")
        receipt = replay_saved(backend, key, kind, payload)
        with backend.connection.cursor() as cursor:
            cursor.execute(
                "select count(*) from WS3_WRITES where write_key=:k and status='DONE'", k=key
            )
            count = cursor.fetchone()[0]
        if count != 1:
            raise ValueError("Expected exactly one completed ledger entry")
        confirmations[kind] = {"status": receipt["status"], "completed_record_count": count}
    records = backend.memory.list_memories(user_id=backend.identity, limit=101)
    if len(records) >= 101:
        raise ValueError("Memory pagination is required for a complete audit")
    memory_key = digest(asdict(review(backend.identity, "memory", payloads["memory"])))
    matched = []
    for item in records:
        record = getattr(item, "record", item)
        metadata = getattr(record, "metadata", {}) or {}
        if metadata.get("write_key") == memory_key:
            if (
                record.content != payloads["memory"]["content"]
                or any(
                    metadata.get(field) != str(payloads["memory"][field])
                    for field in ("identifier", "version", "source_run")
                )
                or metadata.get("approved") != "true"
            ):
                raise ValueError("Approved memory content or provenance differs")
            matched.append(record)
    if len(matched) != 1:
        raise ValueError("Expected exactly one approved procedural memory")
    return {
        "execution_mode": "direct_database_confirmation_audit",
        "run_id": run,
        "confirmations": confirmations,
        "approved_memory_record_count": len(matched),
        "new_case_or_memory_writes": 0,
        "new_embedding_calls": 0,
        "new_agent_runs": 0,
        "passed": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-file", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run = str(UUID(args.run_id))
    output = private_output(args.output)
    settings = Settings.load(args.session_file)
    backend = LiveBackend(settings, getpass("Database password: "), getpass("Wallet password: "))
    try:
        result = audit(backend, args.evidence_root, run)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
        print(json.dumps(result, indent=2))
    finally:
        backend.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit("CONFIRMATION_AUDIT_FAILED " + type(error).__name__) from None
