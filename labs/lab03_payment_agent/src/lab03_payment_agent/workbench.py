"""Presentation models for the learning workbench; never manufacture cloud evidence."""

import json
from pathlib import Path
from uuid import UUID

from .domain import Result

DATA = Path(__file__).resolve().parents[2] / "data"


def contract_library(name="research_contracts.json"):
    if name not in {"contracts.json", "research_contracts.json"}:
        raise ValueError("Unknown workshop manifest")
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def questions():
    return json.loads((DATA / "question_catalog.json").read_text(encoding="utf-8"))


def load_local_report(path):
    path = Path(path).expanduser().resolve()
    if path.is_relative_to(Path(__file__).resolve().parents[4]) or path.stat().st_size > 2_000_000:
        raise ValueError("Choose a private report outside the repository, no larger than 2 MB")
    value = json.loads(path.read_text(encoding="utf-8"))
    UUID(value["run_id"])
    if value["status"] not in {
        "answered",
        "error",
        "conflict",
        "insufficient_evidence",
        "requires_clarification",
    }:
        raise ValueError("Unknown report status")
    if (
        not isinstance(value.get("answer"), str)
        or not isinstance(value.get("telemetry"), dict)
        or any(
            not isinstance(value.get(field), list) for field in ("memories", "citations", "tools")
        )
    ):
        raise ValueError("Malformed report fields")
    result = Result(**value)
    if result.execution_mode not in {"live", "stored_oci_revalidation"}:
        raise ValueError("This viewer requires a retained live OCI report")
    return result


def execution_metrics(result):
    recorded = result.telemetry
    recovered = result.execution_mode == "stored_oci_revalidation"
    original = recorded.get("original_execution", {}) if recovered else recorded
    elapsed = original.get("elapsed_ms")
    return {
        "original_elapsed_seconds": round(elapsed / 1000, 2)
        if isinstance(elapsed, (int, float))
        else None,
        "original_embedding_calls": original.get("embedding_calls"),
        "tool_observations": len(result.tools),
        "contract_sources": len(result.citations),
        "recovered_memories": len(result.memories),
        "model_referenced_memories": len(getattr(result, "memory_references", []))
        if original.get("memory_references_reported")
        else None,
        "tokens": original.get("tokens"),
        "provider_calls": original.get("provider_inference_calls"),
        "new_calls_during_recovery": recorded.get("new_provider_inference_calls")
        if recovered
        else None,
        "recovered": recovered,
        "stages_ms": original.get("stage_latencies_ms", {}),
    }


def payment_facts(result):
    observed = {item["name"]: item["result"] for item in result.tools}
    payment = observed.get("get_payment", {})
    requests = observed.get("find_related_requests", {}).get("requests", [])
    events = observed.get("get_payment_events", {}).get("events", [])
    return {
        "payment_found": payment.get("found"),
        "payment_id": payment.get("payment_id"),
        "request_count": len(requests),
        "distinct_keys": len({item["idempotency_key"] for item in requests}),
        "distinct_payloads": len({item["payload_hash"] for item in requests}),
        "event_count": len(events),
        "requests": requests,
        "events": events,
    }


def learning_checks(result):
    source = result.telemetry.get("original_execution", result.telemetry)
    return [
        {
            "Comprobación": "Respuesta aceptada por el validador",
            "Resultado": result.status == "answered",
        },
        {
            "Comprobación": "Cláusulas contractuales recuperadas",
            "Resultado": bool(result.citations),
        },
        {"Comprobación": "Memoria procedural recuperada", "Resultado": bool(result.memories)},
        {
            "Comprobación": "Tres herramientas observadas",
            "Resultado": {item["name"] for item in result.tools}
            == {"get_payment", "get_payment_events", "find_related_requests"},
        },
        {
            "Comprobación": "Llamada nativa completada",
            "Resultado": source.get("native_call_completed") is True,
        },
    ]
