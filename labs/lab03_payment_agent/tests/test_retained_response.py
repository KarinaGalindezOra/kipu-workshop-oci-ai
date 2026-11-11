"""Retained final answers must remain bound to authenticated database evidence."""

import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from lab03_payment_agent.domain import Request, apply_response, investigate
from lab03_payment_agent.response_format import parse_final_response
from lab03_payment_agent.retained_response import recover


def test_single_explicit_shared_reference_preserves_claim_text():
    original = {
        "finding": "ESCALATE",
        "claims": ["First sentence.", "Second sentence."],
        "evidence_ids": ["E1"],
    }
    parsed = parse_final_response(json.dumps(original))
    assert parsed["claims"] == [
        {"text": text, "evidence_ids": ["E1"]} for text in original["claims"]
    ]


@pytest.mark.parametrize("references", [None, [], ["E1", "E2"], ["E1", "E1"], "E1", [""]])
def test_shared_reference_never_guesses_claim_attribution(references):
    with pytest.raises(ValueError, match="Ambiguous shared citation"):
        parse_final_response(
            json.dumps({"claims": ["First sentence."], "evidence_ids": references})
        )


def test_normalized_claim_still_requires_literal_contractual_support():
    from test_workshop import FakeBackend

    backend = FakeBackend()
    request = Request("Investigate payment idempotency.", "PAY-104", "v2")
    result = investigate(backend, request)
    parsed = parse_final_response(
        json.dumps(
            {
                "finding": "ESCALATE",
                "claims": ["Invented contractual assertion."],
                "evidence_ids": ["E1"],
            }
        )
    )
    with pytest.raises(ValueError, match="Unsupported claim"):
        apply_response(result, request, parsed, result.tools)


def test_offline_report_cannot_be_recovered_as_real_execution(tmp_path):
    run = str(uuid4())
    path = tmp_path / "WS3_P002" / run
    path.mkdir(parents=True)
    (path / "evidence.json").write_text(
        json.dumps(
            {"run_id": run, "status": "error", "execution_mode": "offline_test", "telemetry": {}}
        )
    )
    backend = SimpleNamespace(identity="WS3_P002", settings=SimpleNamespace(db_user="WS3_P002"))
    with pytest.raises(ValueError, match="authentic live failure"):
        recover(
            backend, Request("Investigate payment idempotency.", "PAY-104", "v2"), tmp_path, run
        )


def test_recovery_requires_matching_successful_database_task(tmp_path):
    run = str(uuid4())
    path = tmp_path / "WS3_P002" / run
    path.mkdir(parents=True)
    (path / "evidence.json").write_text(
        json.dumps(
            {
                "run_id": run,
                "status": "error",
                "execution_mode": "live",
                "telemetry": {"select_ai_runs": 1, "native_call_completed": True},
            }
        )
    )
    calls = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def execute(self, sql, **bindings):
            calls.append((sql, bindings))

        def fetchall(self):
            return []

    backend = SimpleNamespace(
        identity="WS3_P002",
        settings=SimpleNamespace(db_user="WS3_P002"),
        connection=SimpleNamespace(cursor=Cursor),
    )
    request = Request("Investigate payment idempotency.", "PAY-104", "v2")
    with pytest.raises(ValueError, match="one successful native task"):
        recover(backend, request, tmp_path, run)
    assert len(calls) == 1
    sql, bindings = calls[0]
    assert "state='SUCCEEDED'" in sql and "DBMS_LOB.INSTR(input,:request)>0" in sql
    assert bindings["request"] == json.dumps(request.__dict__)
    assert run in bindings["run"]
