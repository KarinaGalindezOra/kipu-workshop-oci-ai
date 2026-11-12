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
    app.session_state["query_text"] = (
        "Investigate payment idempotency and prepare a recommendation."
    )
    app.session_state["request_hash"] = digest(
        Request(
            "Investigate payment idempotency and prepare a recommendation.", "PAY-104", "v2"
        ).__dict__
    )
    app.run()
    assert not app.exception
    next(i for i in app.text_input if i.label == "Carpeta privada de evidencias").set_value(
        str(tmp_path)
    ).run()
    buttons = {b.label: b for b in app.button}
    assert buttons["Enviar consulta al agente"].disabled
    assert buttons["Registrar caso"].disabled
    next(c for c in app.checkbox if c.label.startswith("He revisado")).check().run()
    next(b for b in app.button if b.label == "Registrar caso").click().run()
    assert not app.exception
    assert len(backend.saved) == 1
    assert (tmp_path / backend.identity / result.run_id / "case_confirmation.json").exists()
    assert any(b.label == "Guardar memoria aprobada" and b.disabled for b in app.button)
    next(item for item in app.selectbox if item.label == "Pago sintético").select("PAY-105").run()
    assert not any(b.label == "Registrar caso" for b in app.button)
    assert any("Cambiaste los datos de entrada" in w.value for w in app.warning)


def test_dashboard_disconnected_has_no_execution_controls():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui" / "app.py"))
    app.run()
    assert not app.exception
    assert next(b for b in app.button if b.label == "Enviar consulta al agente").disabled
    assert len(app.tabs) == 5


@pytest.mark.parametrize("distance,accepted", [(0.47710963509159976, False), (0.36, True)])
def test_retrieval_reports_rejected_candidates_without_relaxing_threshold(distance, accepted):
    import hashlib
    import json

    contract = json.loads(
        (Path(__file__).resolve().parents[1] / "data/contracts.json").read_text()
    )[1]
    calls = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql, **bindings):
            calls.append((sql, bindings))

        def fetchall(self):
            return [
                (
                    contract["id"],
                    "v2",
                    contract["text"],
                    hashlib.sha256(contract["text"].encode()).hexdigest(),
                    distance,
                )
            ]

    backend = object.__new__(LiveBackend)
    backend.connection = SimpleNamespace(cursor=Cursor)
    backend.settings = SimpleNamespace(threshold=0.470294170237632, embedding_model="model")
    backend.metrics = {}
    backend.embed = lambda text: [1.0, 0.0]
    result = backend.retrieve(Request("Investigate payment idempotency.", "PAY-104", "v2"))
    assert bool(result) is accepted
    assert backend.metrics["rag_candidate_count"] == 1
    assert backend.metrics["rag_accepted_count"] == int(accepted)
    assert backend.metrics["rag_best_distance"] == distance
    assert backend.metrics["rag_distance_threshold"] == 0.470294170237632
    sql, bindings = calls[0]
    assert bindings["version"] == "v2" and bindings["model"] == "model"
    assert bindings["dimension"] == 2
    assert "api_name='payments'" in sql and "corpus_id=:corpus" in sql


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_native_timeout_is_scoped_and_primary_error_survives_cleanup(cleanup_fails):
    primary = RuntimeError("DPY-4024: timeout; private driver details")
    observed_timeouts = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def callfunc(self, *args):
            return "conversation"

        def var(self, *args):
            return SimpleNamespace(getvalue=lambda: "{}")

        def execute(self, sql, **bindings):
            if "RUN_TEAM" in sql:
                observed_timeouts.append(connection.call_timeout)
                raise primary
            if sql.startswith("delete") and cleanup_fails:
                raise RuntimeError("Cleanup failed")

        def fetchall(self):
            return []

    connection = SimpleNamespace(cursor=Cursor, commit=lambda: None, call_timeout=120000)
    backend = object.__new__(LiveBackend)
    backend.connection = connection
    backend.settings = SimpleNamespace()
    backend.readiness = lambda **kwargs: {}
    backend.metrics = {}
    with pytest.raises(RuntimeError) as caught:
        backend.run(Request("Investigate payment idempotency.", "PAY-104", "v2"), {}, "run")
    assert caught.value is primary
    assert observed_timeouts == [300000]
    assert connection.call_timeout == 120000
    assert backend.metrics["native_call_completed"] is False
    assert backend.metrics.get("active_lock_cleanup_failed", False) is cleanup_fails


def test_failed_investigation_retains_only_safe_driver_codes():
    from test_workshop import FakeBackend

    backend = FakeBackend()
    backend.fail = RuntimeError("DPY-4024: private connection information ORA-01013")
    result = investigate(backend, Request("Investigate payment idempotency.", "PAY-104", "v2"))
    assert result.status == "error"
    assert result.telemetry["driver_error_codes"] == ["DPY-4024", "ORA-01013"]
    assert "private connection information" not in str(result.as_dict())


@pytest.mark.parametrize("known", [True, False])
def test_dashboard_explains_only_allowlisted_readiness_failures(monkeypatch, known):
    from streamlit.testing.v1 import AppTest

    message = (
        "A native team run is still RUNNING; inspect server state before retry"
        if known
        else "private connection configuration must never be displayed"
    )

    def fail_load(*args, **kwargs):
        raise ValueError(message)

    monkeypatch.setattr(Settings, "load", fail_load)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "ui/app.py")).run()
    next(b for b in app.button if b.label == "Conectar y verificar preparaci\u00f3n").click().run()
    assert not app.exception
    assert len(app.warning) == int(known)
    if known:
        assert "marcada como RUNNING" in app.warning[0].value
    rendered = " ".join(e.value for e in [*app.error, *app.warning])
    assert "private connection configuration" not in rendered


def test_builder_failure_shows_only_safe_database_code(monkeypatch):
    import lab03_payment_agent.agent_builder as builder
    from streamlit.testing.v1 import AppTest
    from test_workshop import FakeBackend

    monkeypatch.delenv("LAB03_RECOVERY_REVIEW_FILE", raising=False)
    backend = FakeBackend()
    backend.settings = SimpleNamespace(
        db_user=backend.identity,
        manifest_name="research_contracts.json",
        corpus_id="synthetic-payments-research-03",
        agent_team="WS3_LEARN_TEAM",
    )

    def fail(*args):
        raise RuntimeError("ORA-00942: private-credential-sentinel")

    monkeypatch.setattr(builder, "register", fail)
    app = AppTest.from_file(str(Path(__file__).parents[1] / "ui/app.py"))
    app.session_state["backend"] = backend
    app.run()
    next(b for b in app.button if b.label == "Generar definición revisable").click().run()
    next(
        c for c in app.checkbox if c.label.startswith("He revisado y autorizo crear")
    ).check().run()
    next(b for b in app.button if b.label == "Registrar mi agente en ADB").click().run()
    assert not app.exception
    visible = "\n".join(item.value for item in [*app.caption, *app.error])
    assert "ORA-00942" in visible
    assert "private-credential-sentinel" not in visible
