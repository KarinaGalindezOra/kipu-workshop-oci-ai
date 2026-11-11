"""Exercise real idempotency branches while making database writes impossible."""

import json
from types import SimpleNamespace

import pytest
from lab03_payment_agent.confirmation_audit import replay_saved
from lab03_payment_agent.live import LiveBackend


@pytest.mark.parametrize("kind", ["case", "memory"])
def test_saved_confirmation_returns_the_real_noop_without_writing(kind):
    payload = {"source_run": "run", "approved": True}
    backend, cursor, connection = make_backend((json.dumps(payload, sort_keys=True), "DONE"))
    assert replay_saved(backend, "key", kind, payload) == {
        "write_key": "key",
        "status": "already_saved",
    }
    assert backend.connection is connection
    assert len(cursor.executed) == 1
    assert cursor.executed[0].lower().startswith("select ")


@pytest.mark.parametrize("row", [None, (json.dumps({"approved": True}, sort_keys=True), "PENDING")])
def test_missing_or_pending_confirmation_stops_before_insert_lock_or_memory_write(row):
    backend, cursor, connection = make_backend(row)
    with pytest.raises(ValueError, match="before a write or locking"):
        replay_saved(backend, "key", "memory", {"approved": True})
    assert backend.connection is connection
    assert len(cursor.executed) == 1


def test_different_content_is_not_treated_as_a_duplicate():
    backend, cursor, connection = make_backend(
        (json.dumps({"approved": False}, sort_keys=True), "DONE")
    )
    with pytest.raises(ValueError, match="collision"):
        replay_saved(backend, "key", "memory", {"approved": True})
    assert backend.connection is connection
    assert len(cursor.executed) == 1


def make_backend(row):
    class Cursor:
        def __init__(self):
            self.executed = []

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql, **bindings):
            self.executed.append(sql)

        def fetchone(self):
            return row

    cursor = Cursor()
    connection = SimpleNamespace(cursor=lambda: cursor)
    backend = object.__new__(LiveBackend)
    backend.connection = connection
    return backend, cursor, connection
