"""Developer tests only. These doubles are never exposed as participant execution."""

import json
from dataclasses import replace
from unittest.mock import MagicMock

import pytest
from lab02_contract_rag import execution
from lab02_contract_rag import live_validation as live
from lab02_contract_rag.corpus import load_corpus
from lab02_contract_rag.dashboard import (
    expected_comparison,
    list_own_reports,
    load_own_report,
    workshop_cases,
)
from lab02_contract_rag.models import RetrievedEvidence
from lab02_contract_rag.participant import artifact_directory
from lab02_contract_rag.reporting import write_result


@pytest.fixture
def settings():
    return live.LiveLab02Settings(
        "placeholder",
        "model",
        "chat",
        "KHIPU_L2_P001",
        "dsn",
        "wallet",
        2,
        "CHUNKS",
        3,
        "DEFAULT",
        None,
        max_cosine_distance=0.5,
    )


@pytest.fixture
def services(monkeypatch):
    connection = MagicMock()
    monkeypatch.setattr(live, "create_database_connection", lambda *a, **kw: connection)
    client = MagicMock()
    monkeypatch.setattr(live, "create_inference_client", lambda *a: client)
    chunks = load_corpus()
    monkeypatch.setattr(
        live,
        "existing_chunk_hashes",
        lambda *a: {
            c.chunk_id: (c.content_hash, "model", 2, c.embedding_input_hash) for c in chunks
        },
    )
    monkeypatch.setattr(live, "embed_texts", lambda *a: [[1, 2]])

    def retrieve(cursor, table, target, vector, top_k, selected):
        c = next(c for c in chunks if c.contract_version == target and c.section == "Idempotencia")
        return [RetrievedEvidence(c, 0.1, "vector", "cosine_distance")]

    monkeypatch.setattr(live, "retrieve_evidence", retrieve)
    monkeypatch.setattr(
        live,
        "generate_grounded_answer",
        lambda client, s, q, e: {
            "status": "answered",
            "claims": [{"text": e[0].chunk.content, "evidence_ids": ["E1"]}],
        },
    )
    return connection


def test_real_path_has_service_trace_and_never_publishes_reference_answer(
    settings, services, tmp_path
):
    case = next(c for c in workshop_cases() if c["id"] == "T04")
    result = execution.execute_live(
        settings, case["question"], confirm_inference=True, output_root=tmp_path
    )
    assert result["status"] == "answered" and result["cloud_executed"]
    assert result["execution_origin"] == "oci_services"
    assert result["telemetry"]["chat_calls"] == 1
    assert result["telemetry"]["query_embedding_calls"] == 1
    assert expected_comparison(result)["assessment"]["passed"]
    explicit_scope = {**result, "request_controls": {"version": "v2", "compare": False}}
    assert expected_comparison(explicit_scope)["assessment"]["passed"]
    path = list_own_reports(tmp_path, "p001")[0]
    assert load_own_report(tmp_path, "p001", path)["answer"] == result["answer"]


def test_inference_requires_opt_in_before_network(settings, monkeypatch):
    monkeypatch.setattr(
        live, "create_inference_client", lambda *a: pytest.fail("No client allowed")
    )
    with pytest.raises(ValueError, match="acknowledgement"):
        execution.execute_live(settings, "In v2, what endpoint?", confirm_inference=False)


def test_unsupported_documentary_question_really_retrieves(settings, services):
    result = execution.execute_live(
        settings, "En v2, ¿qué SLA se garantiza?", confirm_inference=True
    )
    assert result["status"] == "insufficient_evidence"
    assert result["telemetry"]["query_embedding_calls"] == 1
    assert result["telemetry"]["chat_calls"] == 0
    assert any(t["service_operation"] == "adb_vector_search" for t in result["service_trace"])


def test_clarification_is_never_claimed_as_model_output(settings, monkeypatch):
    monkeypatch.setattr(live, "create_database_connection", lambda *a, **kw: pytest.fail("No DB"))
    result = execution.execute_live(settings, "¿Cómo actualizo el estado?", confirm_inference=False)
    assert result["status"] == "needs_clarification"
    assert result["execution_origin"] == "application_control"
    assert not result["cloud_executed"] and not result["answer"]


def test_model_failure_has_no_local_fallback(settings, services, monkeypatch):
    def fail(*args):
        raise RuntimeError("SECRET_MUST_NOT_BE_RECORDED")

    monkeypatch.setattr(live, "generate_grounded_answer", fail)
    result = execution.execute_live(
        settings, "En v2, ¿qué header de idempotencia?", confirm_inference=True
    )
    assert result["status"] == "error" and not result["answer"]
    assert "SECRET_MUST_NOT_BE_RECORDED" not in json.dumps(result)
    assert result["service_trace"][-1]["status"] == "failed"
    assert result["service_trace"][-1]["safe_error_code"] == "RuntimeError"


def test_missing_corpus_never_inserts_without_independent_ack(settings, services, monkeypatch):
    monkeypatch.setattr(live, "existing_chunk_hashes", lambda *a: {})
    monkeypatch.setattr(live, "insert_chunks", lambda *a: pytest.fail("Insert not authorized"))
    result = execution.execute_live(settings, "In v2, what endpoint?", confirm_inference=True)
    assert result["status"] == "error" and result["telemetry"]["document_embedding_calls"] == 0


def test_positive_load_ack_uses_real_adapter_and_commit(settings, services, monkeypatch):
    monkeypatch.setattr(live, "existing_chunk_hashes", lambda *a: {})
    inserted = []
    monkeypatch.setattr(live, "insert_chunks", lambda *a: inserted.extend(a[2]))
    result = execution.execute_live(
        settings, "Prepare corpus", confirm_inference=True, confirm_load=True, ingest_only=True
    )
    assert result["status"] == "ingested" and len(inserted) == 9
    assert result["telemetry"]["document_embedding_calls"] == 1
    services.__enter__.return_value.commit.assert_called_once()


def test_comparison_embeds_question_once(settings, services, monkeypatch):
    monkeypatch.setattr(
        live,
        "generate_grounded_answer",
        lambda client, s, q, e: {
            "status": "answered",
            "claims": [
                {"text": i.chunk.content, "evidence_ids": [f"E{n}"]} for n, i in enumerate(e, 1)
            ],
        },
    )
    result = execution.execute_live(
        settings, "Compara los headers de idempotencia entre v1 y v2.", confirm_inference=True
    )
    assert result["telemetry"]["query_embedding_calls"] == 1
    assert sum(t["service_operation"] == "adb_vector_search" for t in result["service_trace"]) == 2


def test_report_reader_rejects_peer_and_local_reports(settings, services, tmp_path):
    result = execution.execute_live(
        settings, "En v2, ¿qué header de idempotencia?", confirm_inference=True
    )
    peer = write_result(artifact_directory(tmp_path, "p002"), {**result, "participant_id": "p002"})
    with pytest.raises(ValueError, match="namespace"):
        load_own_report(tmp_path, "p001", peer)
    own = write_result(artifact_directory(tmp_path, "p001"), {**result, "mode": "local"})
    with pytest.raises(ValueError, match="real-workflow"):
        load_own_report(tmp_path, "p001", own)
    assert not list_own_reports(tmp_path, "p001")


def test_real_workshop_matrix_contains_no_simulated_fixtures():
    cases = workshop_cases()
    assert len(cases) == 16
    assert not {"T16", "T17", "T18", "T20"} & {c["id"] for c in cases}


def test_custom_request_is_not_falsely_compared_against_another_question():
    result = {"question": "Custom question"}
    assert expected_comparison(result) is None
    assert expected_comparison({"request_controls": {"version": "v2"}}) is None


def test_id_mismatch_fails_before_services(settings):
    with pytest.raises(ValueError, match="identity"):
        execution.execute_live(
            replace(settings, participant_id="p002"), "In v2, endpoint?", confirm_inference=True
        )
