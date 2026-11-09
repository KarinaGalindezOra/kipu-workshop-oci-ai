"""Driver/SDK boundaries and dashboard workflow without network access."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from lab03_payment_agent.domain import RULE, Request, investigate
from lab03_payment_agent.live import LiveBackend, Settings, parse_final_response


@pytest.mark.parametrize("wrapper", ["{}", "```json\n{}", "```json\n{}\n```"])
def test_final_json_presentation_and_scalar_reference_preserve_content(wrapper):
    import json

    value = {"finding": "ESCALATE", "claims": [{"text": "Exact quote.", "evidence_id": "E1"}]}
    parsed = parse_final_response(wrapper.format(json.dumps(value)))
    assert parsed == {
        "finding": "ESCALATE",
        "claims": [{"text": "Exact quote.", "evidence_ids": ["E1"]}],
    }


@pytest.mark.parametrize(
    "raw",
    [
        'Commentary {"finding":"ESCALATE"}',
        '```json\n{"finding":"ESCALATE"}\n```\nExtra commentary',
        '{"finding":"ESCALATE","finding":"NO_DUPLICATE_EVIDENCE"}',
        '{"claims":[{"evidence_id":"E1","evidence_ids":["E2"]}]}',
        '{"claims":[{"evidence_id":["E1"]}]}',
        '```json\n{"finding":ESCALATE}',
        "[]",
    ],
)
def test_final_response_does_not_repair_ambiguous_or_invalid_content(raw):
    with pytest.raises(ValueError):
        parse_final_response(raw)


@pytest.mark.parametrize("reviewed", [frozenset(), frozenset({"previous-run"})])
def test_readiness_blocks_retry_while_native_team_is_running(reviewed):
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql):
            assert "USER_AI_AGENT_TEAM_HISTORY" in sql
            assert "RUNNING" in sql

        def fetchall(self):
            return [("native-run",)]

    backend = object.__new__(LiveBackend)
    backend.connection = SimpleNamespace(cursor=Cursor)
    with pytest.raises(ValueError, match="still RUNNING"):
        backend.readiness(reviewed_stopped_runs=reviewed)


def test_reviewed_orphan_does_not_authorize_a_new_running_execution():
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql):
            assert "USER_AI_AGENT_TEAM_HISTORY" in sql

        def fetchall(self):
            return [("reviewed-orphan",), ("unreviewed-new-run",)]

    backend = object.__new__(LiveBackend)
    backend.connection = SimpleNamespace(cursor=Cursor)
    with pytest.raises(ValueError, match="still RUNNING"):
        backend.readiness(reviewed_stopped_runs=frozenset({"reviewed-orphan"}))


def test_real_sdk_search_result_unwraps_record_metadata():
    from oracleagentmemory.apis.records import GuidelineRecord

    matched = GuidelineRecord(
        id="seed",
        content=RULE,
        user_id="WS3_P001",
        metadata={"identifier": "seed", "version": "v2", "approved": "true"},
    )
    wrapper = SimpleNamespace(record=matched, content=RULE)
    calls = []

    def search(query, **kwargs):
        calls.append(kwargs)
        return [wrapper]

    backend = object.__new__(LiveBackend)
    backend.identity = "WS3_P001"
    backend.memory = SimpleNamespace(search=search)
    result = backend.memories("payment idempotency")
    assert result[0].approved
    assert result[0].version == "v2"
    assert calls[0]["user_id"] == backend.identity
    assert calls[0]["exact_user_match"] is True


def test_configuration_cannot_inherit_a_previous_tenant(tmp_path, monkeypatch):
    monkeypatch.setenv("OCI_REGION", "previous-region")
    path = tmp_path / "participant.env"
    path.write_text("LAB03_PARTICIPANT_ID=p001\nLAB03_WALLET_DIR=wallet\nLAB03_DB_DSN=service\n")
    with pytest.raises(ValueError, match="OCI_REGION"):
        Settings.load(path, require_calibration=False)


@pytest.mark.parametrize("participant", ["p000", "p016", "p999", "p001;drop"])
def test_assignment_is_bounded(tmp_path, participant):
    path = tmp_path / "participant.env"
    path.write_text("LAB03_PARTICIPANT_ID=" + participant)
    with pytest.raises(ValueError, match="Participant"):
        Settings.load(path, require_calibration=False)


def test_dashboard_gates_writes_and_invalidates_changed_input(tmp_path):
    from streamlit.testing.v1 import AppTest
    from test_workshop import FakeBackend

    backend = FakeBackend()
    result = investigate(backend, Request("Investigate payment idempotency.", "PAY-104", "v2"))
    result.execution_mode = "offline_test"
    from lab03_payment_agent.domain import digest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui" / "app.py"))
    app.session_state["backend"] = backend
    app.session_state["result"] = result
    app.session_state["request_hash"] = digest(
        Request(
            "Investigate payment idempotency and prepare a recommendation.", "PAY-104", "v2"
        ).__dict__
    )
    app.run()
    assert not app.exception
    next(i for i in app.text_input if i.label == "Private evidence directory").set_value(
        str(tmp_path)
    ).run()
    buttons = {b.label: b for b in app.button}
    assert buttons["Run investigation"].disabled
    assert buttons["Register case"].disabled
    next(c for c in app.checkbox if c.label.startswith("I reviewed")).check().run()
    next(b for b in app.button if b.label == "Register case").click().run()
    assert not app.exception
    assert len(backend.saved) == 1
    assert (tmp_path / backend.identity / result.run_id / "case_confirmation.json").exists()
    assert any(b.label == "Save approved memory" and b.disabled for b in app.button)
    app.selectbox[0].select("PAY-105").run()
    assert not any(b.label == "Register case" for b in app.button)
    assert any("Inputs changed" in w.value for w in app.warning)


def test_dashboard_disconnected_has_no_execution_controls():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui" / "app.py"))
    app.run()
    assert not app.exception
    assert not any(b.label == "Run investigation" for b in app.button)
