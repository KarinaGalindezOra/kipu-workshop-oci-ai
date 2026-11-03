"""Tests for the no-inference ADB readiness check."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "validate_environment.py"
SPEC = importlib.util.spec_from_file_location("lab02_validate_environment", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_database_check_closes_checked_connection(monkeypatch, capsys):
    closed = False

    class Connection:
        def close(self):
            nonlocal closed
            closed = True

    monkeypatch.setattr(MODULE, "settings_from_environment", lambda **_: object())
    monkeypatch.setattr(MODULE, "create_database_connection", lambda _: Connection())

    MODULE.validate_database()

    assert closed is True
    assert '"database_session": "participant_schema"' in capsys.readouterr().out
