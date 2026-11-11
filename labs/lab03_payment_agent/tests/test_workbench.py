"""Learning views distinguish authored fixtures, recorded metrics and live acceptance."""

import json

import pytest
from lab03_payment_agent.domain import Request, Result, apply_response, investigate
from lab03_payment_agent.workbench import (
    DATA,
    contract_library,
    execution_metrics,
    load_local_report,
)


def test_expanded_corpus_is_additive_and_quotes_real_fixture_lines():
    old = contract_library("contracts.json")
    new = contract_library()
    assert len(old) == 2 and len(new) == 12
    assert not {item["id"] for item in old}.intersection(item["id"] for item in new)
    assert len({item["id"] for item in new}) == 12
    for item in new:
        source = (DATA / item["source_file"]).read_text(encoding="utf-8").splitlines()
        assert "\n".join(source[item["line_start"] - 1 : item["line_end"]]) == item["text"]
        assert item["source_uri"].startswith("synthetic://payments/research/")


def test_local_library_does_not_accept_arbitrary_paths():
    with pytest.raises(ValueError):
        contract_library("../../private.json")


def test_recovery_metrics_keep_original_duration_and_do_not_invent_usage():
    result = Result(
        execution_mode="stored_oci_revalidation",
        telemetry={
            "original_execution": {"elapsed_ms": 100481, "embedding_calls": 1},
            "new_provider_inference_calls": 0,
        },
    )
    metrics = execution_metrics(result)
    assert metrics["original_elapsed_seconds"] == 100.48
    assert metrics["original_embedding_calls"] == 1 and metrics["new_calls_during_recovery"] == 0
    assert metrics["tokens"] is None and metrics["provider_calls"] is None
    assert metrics["model_referenced_memories"] is None


def test_local_viewer_rejects_offline_results(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps(Result(execution_mode="offline_test").as_dict()))
    with pytest.raises(ValueError, match="live OCI"):
        load_local_report(path)


def test_observers_and_phase_timings_do_not_expose_internal_reasoning():
    from test_workshop import FakeBackend

    events = []
    result = investigate(
        FakeBackend(),
        Request("Investigate payment idempotency.", "PAY-104", "v2"),
        observer=events.append,
    )
    assert events == ["memory", "retrieval", "agent", "validation"]
    assert set(result.telemetry["stage_latencies_ms"]) == set(events)
    assert all(value >= 0 for value in result.telemetry["stage_latencies_ms"].values())


def test_unknown_memory_reference_is_rejected():
    from test_workshop import FakeBackend

    backend = FakeBackend()
    request = Request("Investigate payment idempotency.", "PAY-104", "v2")
    result = investigate(backend, request)
    response, observations = backend.run(request, {}, result.run_id)
    response["memory_ids"] = ["invented-memory"]
    with pytest.raises(ValueError, match="Unverified memory"):
        apply_response(result, request, response, observations)


def test_new_native_task_references_only_supplied_memories():
    from test_workshop import FakeBackend

    backend = FakeBackend()
    request = Request("Investigate payment idempotency.", "PAY-104", "v2")
    result = investigate(backend, request)
    response, observations = backend.run(request, {}, result.run_id)
    response["memory_ids"] = ["seed"]
    assert apply_response(result, request, response, observations).memory_references == ["seed"]


def test_disconnected_workbench_teaches_construction_without_enabling_cloud_actions():
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).parents[1] / "ui/app.py")).run()
    next(
        button for button in app.button if button.label == "Generar definición revisable"
    ).click().run()
    assert not app.exception
    assert len(app.session_state["blueprint"].objects()) == 6
    assert next(
        button for button in app.button if button.label == "Registrar mi agente en ADB"
    ).disabled
    assert next(
        button for button in app.button if button.label == "Enviar consulta al agente"
    ).disabled
    assert len(app.metric) == 0


def test_loading_retained_report_shows_recorded_metrics_without_confirmations():
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    result = Result(
        status="error",
        answer="Retained failure.",
        execution_mode="stored_oci_revalidation",
        telemetry={
            "original_execution": {"elapsed_ms": 100481, "embedding_calls": 1},
            "new_provider_inference_calls": 0,
        },
    )
    app = AppTest.from_file(str(Path(__file__).parents[1] / "ui/app.py")).run()
    app.session_state["inspection_result"] = result
    app.run()
    assert not app.exception
    metrics = {item.label: item.value for item in app.metric}
    assert metrics["Duración original"] == "100.48 s"
    assert metrics["Tokens reportados"] == "No disponible"
    assert not {"Registrar caso", "Guardar memoria aprobada"}.intersection(
        b.label for b in app.button
    )


@pytest.mark.parametrize(
    "manifest,corpus,team",
    [
        ("../private.json", "synthetic-payments-03", "WS3_TEAM"),
        ("research_contracts.json", "synthetic-payments-03", "WS3_LEARN_TEAM"),
        ("contracts.json", "synthetic-payments-03", "OTHER_TEAM"),
    ],
)
def test_configuration_rejects_unapproved_corpus_and_team(tmp_path, manifest, corpus, team):
    from lab03_payment_agent.live import Settings

    path = tmp_path / "assignment.env"
    path.write_text(
        "LAB03_PARTICIPANT_ID=p001\n"
        + f"LAB03_CORPUS_MANIFEST={manifest}\nLAB03_CORPUS_ID={corpus}\nLAB03_AGENT_TEAM={team}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="approved manifest/corpus"):
        Settings.load(path, require_calibration=False)
