"""Small, extractive acceptance boundary independent of model/provider SDKs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol
from uuid import uuid4

from lab02_contract_rag.evidence import UNSUPPORTED, citations
from lab02_contract_rag.models import ContractChunk, RetrievedEvidence

CORPUS = "synthetic-payments-03"
TOOLS = {"get_payment", "get_payment_events", "find_related_requests"}
RULE = "For payment idempotency, reject a repeated request with a different payload; preserve the original request identifier and escalate for investigation."
LEARNED_RULE = "Before escalating a payment idempotency conflict, compare the related request payload hashes and preserve the original request identifier."


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Request:
    question: str
    payment_id: str
    version: str

    def validate(self) -> None:
        if not self.question.strip() or len(self.question) > 1500:
            raise ValueError("Question must contain 1 to 1500 characters")
        if not re.fullmatch(r"PAY-[0-9]{3}", self.payment_id):
            raise ValueError("Payment identifier must match PAY-000")
        if self.version not in {"v1", "v2"}:
            raise ValueError("Choose an explicit contract version")


@dataclass(frozen=True)
class Memory:
    identifier: str
    content: str
    version: str
    source_run: str
    approved: bool = True


@dataclass
class Result:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "error"
    answer: str = ""
    memories: list[dict] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    tools: list[dict] = field(default_factory=list)
    proposal: dict | None = None
    telemetry: dict = field(default_factory=lambda: {"tokens": None, "token_source": "unavailable"})
    execution_mode: str = "live"

    memory_references: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        value = asdict(self)
        if not self.memory_references:
            value.pop("memory_references")
        return value


class Backend(Protocol):
    identity: str

    def memories(self, query: str) -> list[Memory]: ...
    def retrieve(self, request: Request) -> list[RetrievedEvidence]: ...
    def run(self, request: Request, context: dict, run_id: str) -> tuple[dict, list[dict]]: ...


def validate_sources(
    items: list[RetrievedEvidence], version: str, corpus: str = CORPUS
) -> list[dict]:
    for item in items:
        c = item.chunk
        if (c.corpus_id, c.api_name, c.contract_version, c.data_classification) != (
            corpus,
            "payments",
            version,
            "synthetic",
        ):
            raise ValueError("Evidence scope mismatch")
        if hashlib.sha256(c.content.encode()).hexdigest() != c.content_hash:
            raise ValueError("Evidence hash mismatch")
    return citations(items)


def exact_sentence_span(text: str, excerpt: str) -> bool:
    separators = list(re.finditer(r"(?<=[.!?])\s+", excerpt))
    starts = [0, *[m.end() for m in separators]]
    ends = [*[m.start() for m in separators], len(excerpt)]
    return any(text == excerpt[start:end] for start in starts for end in ends if end > start)


def apply_response(
    result: Result, request: Request, response: dict, observations: list[dict]
) -> Result:
    """Validate actual tool observations and extractive claims without invoking a model."""
    sources = result.citations
    result.tools = observations
    if not observations or any(
        o.get("name") not in TOOLS
        or o.get("payment_id") != request.payment_id
        or o.get("run_id") != result.run_id
        or not isinstance(o.get("result"), dict)
        for o in observations
    ):
        raise ValueError("Unverified tool output")
    by_name = {o["name"]: o["result"] for o in observations}
    if "get_payment" not in by_name:
        raise ValueError("Payment lookup missing")
    if not isinstance(by_name["get_payment"].get("found"), bool):
        raise ValueError("Invalid payment lookup result")
    if not by_name["get_payment"].get("found"):
        result.status = "insufficient_evidence"
        result.answer = "Synthetic payment not found. No case was proposed."
        return result
    if set(by_name) != TOOLS:
        raise ValueError("Required tools missing")
    requests = by_name["find_related_requests"].get("requests", [])
    if not requests or not by_name["get_payment_events"].get("events"):
        result.status = "insufficient_evidence"
        result.answer = "Requests and payment events are required."
        return result
    keys = {r["idempotency_key"] for r in requests}
    hashes = {r["payload_hash"] for r in requests}
    expected = (
        "ESCALATE"
        if len(requests) > 1 and len(keys) == 1 and len(hashes) > 1
        else "NO_DUPLICATE_EVIDENCE"
    )
    if response.get("finding") != expected:
        raise ValueError("Finding disagrees with observed requests")
    claims = response.get("claims", [])
    evidence = {s["evidence_id"]: s for s in sources}
    if not claims or len(claims) > 3:
        raise ValueError("Contractual claims missing")
    for claim in claims:
        text, ids = claim.get("text", ""), claim.get("evidence_ids", [])
        if (
            not text.strip()
            or not ids
            or any(
                i not in evidence or not exact_sentence_span(text, evidence[i]["excerpt"])
                for i in ids
            )
        ):
            raise ValueError("Unsupported claim")
    if "memory_ids" in response:
        references = response["memory_ids"]
        available = {memory["identifier"] for memory in result.memories}
        if (
            not isinstance(references, list)
            or any(not isinstance(item, str) or item not in available for item in references)
            or len(references) != len(set(references))
        ):
            raise ValueError("Unverified memory reference")
        result.memory_references = references
    result.status = "answered"
    # Do not publish free-form model narration or its hidden reasoning.
    result.answer = (
        expected
        + "\n"
        + "\n".join(c["text"] + " [" + ", ".join(c["evidence_ids"]) + "]" for c in claims)
    )
    if expected == "ESCALATE":
        result.proposal = {
            "run_id": result.run_id,
            "payment_id": request.payment_id,
            "version": request.version,
            "finding": expected,
            "request_ids": sorted(r["request_id"] for r in requests),
        }
    return result


def investigate(backend: Backend, request: Request, observer=None) -> Result:
    """Accept only extractive claims and tool-derived, domain-bounded findings."""
    from time import perf_counter

    result = Result()
    started = perf_counter()
    stages = {}
    active_stage = None
    phase = started
    try:
        request.validate()
    except ValueError:
        result.status = "requires_clarification"
        result.answer = "Provide a question, a synthetic payment identifier and v1 or v2."
        return result
    try:
        if hasattr(backend, "metrics"):
            backend.metrics.clear()
        if UNSUPPORTED.search(request.question):
            result.status = "insufficient_evidence"
            result.answer = "The synthetic payment corpus does not support this topic."
            return result
        result.telemetry["stage_latencies_ms"] = stages
        active_stage = "memory"
        if observer:
            observer("memory")
        phase = perf_counter()
        memories = backend.memories("payment idempotency")
        stages["memory"] = round((perf_counter() - phase) * 1000)
        result.memories = [asdict(m) for m in memories]
        active_stage = "retrieval"
        if observer:
            observer("retrieval")
        phase = perf_counter()
        corpus = getattr(getattr(backend, "settings", None), "corpus_id", CORPUS)
        sources = validate_sources(backend.retrieve(request), request.version, corpus)
        stages["retrieval"] = round((perf_counter() - phase) * 1000)
        result.citations = sources
        if not sources or not memories:
            result.status = "insufficient_evidence"
            result.answer = (
                "No contractual evidence passed retrieval validation."
                if memories and not sources
                else "An approved procedure and contractual evidence are required."
            )
            return result
        # This exercise accepts one explicit procedure. Unrecognized edits require review;
        # keyword presence alone cannot establish policy compatibility.
        if any(
            not m.approved or m.version != "v2" or m.content not in {RULE, LEARNED_RULE}
            for m in memories
        ):
            result.status = "conflict"
            result.answer = "Review the memory against the approved v2 procedure."
            return result
        if request.version != "v2":
            result.status = "conflict"
            result.answer = "The approved memory applies to v2, not this contract."
            return result
        context = {"memories": result.memories, "sources": sources}
        active_stage = "agent"
        if observer:
            observer("agent")
        phase = perf_counter()
        response, observations = backend.run(request, context, result.run_id)
        stages["agent"] = round((perf_counter() - phase) * 1000)
        active_stage = "validation"
        if observer:
            observer("validation")
        phase = perf_counter()
        validated = apply_response(result, request, response, observations)
        stages["validation"] = round((perf_counter() - phase) * 1000)
        return validated
    except Exception as exc:
        if active_stage:
            stages[active_stage] = round((perf_counter() - phase) * 1000)
        partial = getattr(backend, "last_observations", [])
        if isinstance(partial, list):
            result.tools = [
                o
                for o in partial
                if isinstance(o, dict)
                and o.get("name") in TOOLS
                and o.get("payment_id") == request.payment_id
                and o.get("run_id") == result.run_id
                and isinstance(o.get("result"), dict)
            ]
        # SDK/driver errors can contain endpoints, credentials or SQL text.
        result.telemetry["error_type"] = type(exc).__name__
        result.telemetry["driver_error_codes"] = sorted(
            set(re.findall(r"\b(?:DPY|DPI|ORA|TNS)-\d{3,5}\b", str(exc)))
        )
        code = getattr(exc.args[0], "code", None) if exc.args else None
        if isinstance(code, int):
            result.telemetry["database_error_code"] = code
        result.status = "error"
        result.answer = (
            "Execution failed. Check readiness and retry explicitly; no automatic write occurred."
        )
        result.proposal = None
    finally:
        result.telemetry.update(getattr(backend, "metrics", {}))
        result.telemetry["elapsed_ms"] = round((perf_counter() - started) * 1000)
    return result


def chunk(
    identifier: str, version: str, content: str, *, corpus_id=CORPUS, metadata=None
) -> ContractChunk:
    metadata = metadata or {}
    return ContractChunk(
        chunk_id=identifier,
        contract_version=version,
        content=content,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        source_uri=metadata.get("source_uri", f"synthetic://payments/{version}/idempotency"),
        section=metadata.get("section", "Idempotency"),
        corpus_id=corpus_id,
        api_name="payments",
        document_id=metadata.get("document_id", ""),
        source_title=metadata.get("title", "Synthetic Payments Contract"),
        line_start=metadata.get("line_start", 0),
        line_end=metadata.get("line_end", 0),
    )
