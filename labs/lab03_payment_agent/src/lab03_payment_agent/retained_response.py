"""Revalidate a completed native answer without another embedding or agent call."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from uuid import UUID

from lab02_contract_rag.models import RetrievedEvidence

from .domain import CORPUS, LEARNED_RULE, RULE, Result, apply_response, chunk, validate_sources
from .response_format import parse_final_response


def recover(backend, request, evidence_root: Path, source_run: str):
    """Require the retained live failure, exact successful DB task and original facts."""
    run = str(UUID(source_run))
    request.validate()
    root = evidence_root.expanduser().resolve()
    if root.is_relative_to(Path(__file__).resolve().parents[4]):
        raise ValueError("Retained evidence must remain outside the repository")
    path = root / backend.identity / run / "evidence.json"
    source = path.read_bytes()
    original = json.loads(source)
    metrics = original.get("telemetry", {})
    if (
        original.get("run_id") != run
        or original.get("execution_mode") != "live"
        or original.get("status") != "error"
        or metrics.get("select_ai_runs") != 1
        or metrics.get("native_call_completed") is not True
        or backend.identity != backend.settings.db_user
    ):
        raise ValueError("A completed native call and an authentic live failure are required")
    with backend.connection.cursor() as cursor:
        cursor.execute(
            "select result from USER_AI_AGENT_TASK_HISTORY where state='SUCCEEDED' "
            "and DBMS_LOB.INSTR(input,:run)>0 and DBMS_LOB.INSTR(input,:request)>0",
            run='"run_id": "' + run + '"',
            request=json.dumps(request.__dict__, ensure_ascii=False),
        )
        rows = cursor.fetchall()
        if len(rows) != 1:
            raise ValueError("Require one successful native task for this exact request and run")
        value = rows[0][0]
        raw = value.read() if hasattr(value, "read") else value
        if len(raw) != metrics.get("native_response_characters"):
            raise ValueError("Stored native final response differs from the observed call")
        cursor.execute(
            "select tool_name,payment_id,payload from WS3_TOOL_LOG where run_id=:r order by logged_at",
            r=run,
        )
        observations = [
            {
                "run_id": run,
                "name": name,
                "payment_id": payment,
                "result": json.loads(payload.read() if hasattr(payload, "read") else payload),
            }
            for name, payment, payload in cursor.fetchall()
        ]
        if observations != original["tools"]:
            raise ValueError("Retained observations differ from the authenticated database trace")
        manifest = {
            item["id"]: item
            for item in json.loads(
                (Path(__file__).resolve().parents[2] / "data/contracts.json").read_text()
            )
        }
        items = []
        for citation in original["citations"]:
            canonical = manifest[citation["chunk_id"]]
            contract = chunk(canonical["id"], canonical["version"], canonical["text"])
            cursor.execute(
                "select content,content_hash,corpus_id,api_name,contract_version "
                "from WS3_CHUNKS where chunk_id=:i and embedding_model=:m",
                i=contract.chunk_id,
                m=backend.settings.embedding_model,
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Contract evidence missing")
            text = row[0].read() if hasattr(row[0], "read") else row[0]
            if (text, *row[1:]) != (
                contract.content,
                contract.content_hash,
                CORPUS,
                "payments",
                request.version,
            ) or citation["rank_value"] > backend.settings.threshold:
                raise ValueError("Contract scope, content or retrieval threshold differs")
            items.append(
                RetrievedEvidence(
                    contract, citation["rank_value"], citation["method"], citation["score_type"]
                )
            )
    if validate_sources(items, request.version) != original["citations"]:
        raise ValueError("Retained citations differ from the canonical scoped contract")
    current = [asdict(memory) for memory in backend.memories("payment idempotency")]
    if not original["memories"] or any(
        memory not in current
        or not memory["approved"]
        or memory["version"] != "v2"
        or memory["content"] not in {RULE, LEARNED_RULE}
        for memory in original["memories"]
    ):
        raise ValueError("Approved memory provenance differs")
    result = Result(**original)
    result.execution_mode = "stored_oci_revalidation"
    result.telemetry = {
        "source_run_id": run,
        "source_evidence_sha256": hashlib.sha256(source).hexdigest(),
        "native_final_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "native_task_succeeded": True,
        "original_execution": metrics,
        "new_embedding_calls": 0,
        "new_select_ai_runs": 0,
        "new_provider_inference_calls": 0,
        "tokens": None,
        "token_source": "unavailable",
    }
    apply_response(result, request, parse_final_response(raw), observations)
    if result.status != "answered":
        raise ValueError("Retained response failed the same semantic acceptance boundary")
    target = path.with_name("evidence.revalidated.json")
    encoded = json.dumps(result.as_dict(), indent=2)
    if target.exists():
        if target.read_text(encoding="utf-8") != encoded:
            raise ValueError("Preserve the existing revalidation evidence")
    else:
        with target.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    return result
