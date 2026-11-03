from pathlib import Path

import pytest
from lab02_contract_rag import private_session


def test_private_session_loads_dotenv_without_shell_execution(tmp_path, monkeypatch):
    session = tmp_path / "participant.env"
    session.write_text("LAB02_PARTICIPANT_ID=p001\n", encoding="utf-8")
    calls = []
    monkeypatch.setattr(
        private_session,
        "load_dotenv",
        lambda path=None, override=False: calls.append((path, override)),
    )

    assert private_session.load_participant_session(session) == session.resolve()
    assert calls == [(session.resolve(), True)]


def test_private_session_rejects_password_or_secret_values(tmp_path):
    session = tmp_path / "participant.env"
    session.write_text("ADB_SCHEMA_PASSWORD=not-allowed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must not contain passwords or secrets"):
        private_session.load_participant_session(session)


def test_private_session_requires_existing_file(tmp_path):
    with pytest.raises(ValueError, match="unavailable"):
        private_session.load_participant_session(Path(tmp_path / "missing.env"))
