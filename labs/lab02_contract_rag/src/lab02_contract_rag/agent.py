"""Bounded RAG orchestration with strict scope and extractive claim verification.

This MVP intentionally accepts verbatim claims only. Arbitrary paraphrase entailment
requires independent semantic review and is not certified by citation presence.
"""

import re
import time
from collections.abc import Callable
from uuid import uuid4

from .evidence import citations, requested_facets, section_facet, select_evidence
from .models import RetrievedEvidence

Retriever = Callable[[str, str], list[RetrievedEvidence]]
Generator = Callable[[str, list[RetrievedEvidence]], dict]
STATES = {
    "answered",
    "partial",
    "needs_clarification",
    "insufficient_evidence",
    "conflicting_evidence",
    "structured_data_required",
    "error",
}


def resolve_request(question: str, version: str | None = None, compare: bool = False):
    mentioned = set(re.findall(r"\bv\d+\b", question.lower()))
    if version and version not in {"v1", "v2"} or mentioned - {"v1", "v2"}:
        return [], "insufficient_evidence", "Requested version is not in the corpus."
    if compare or re.search(r"\bcompar|\bbetween\b|\bdifference", question, re.I):
        return ["v1", "v2"], None, ""
    if len(mentioned) > 1:
        if re.search(r"migrat|moving|\bto v2\b", question, re.I):
            if version and version != "v2":
                return (
                    [],
                    "needs_clarification",
                    "Selected version conflicts with migration target.",
                )
            return ["v2"], None, ""
        if version:
            return [version], None, ""
        target = re.match(r"\s*(?:in|for)\s+(v[12])\b", question, re.I)
        if target:
            return [target.group(1).lower()], None, ""
        return [], "needs_clarification", "Choose a target version or comparison mode."
    if version and mentioned and version not in mentioned:
        return [], "needs_clarification", "Selected version conflicts with the question."
    versions = [version] if version else sorted(mentioned)
    if not versions:
        return [], "needs_clarification", "Which contract version: v1 or v2?"
    return versions, None, ""


def validate_generation(payload: dict, sources: list[dict]) -> list[dict]:
    if not isinstance(payload, dict) or payload.get("status") not in {
        "answered",
        "partial",
        "insufficient_evidence",
    }:
        raise ValueError("Invalid generation status")
    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Claims must be a list")
    if payload["status"] == "insufficient_evidence":
        if claims:
            raise ValueError("Abstention cannot contain claims")
        return []
    if not claims:
        raise ValueError("Answered output requires supported claims")
    by_id = {item["evidence_id"]: item for item in sources}
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Invalid claim")
        text, ids = claim.get("text"), claim.get("evidence_ids")
        if not isinstance(text, str) or not text.strip() or not isinstance(ids, list) or not ids:
            raise ValueError("Claim requires text and evidence IDs")
        for evidence_id in ids:
            if not isinstance(evidence_id, str) or evidence_id not in by_id:
                raise ValueError("Unknown evidence ID")
            excerpt = by_id[evidence_id]["excerpt"]
            sentences = re.split(r"(?<=[.!?])\s+", excerpt)
            if text != excerpt and text not in sentences:
                raise ValueError("Claim is not a verbatim supported excerpt")
    return claims


def run_agent(
    question: str,
    retriever: Retriever,
    *,
    version: str | None = None,
    compare: bool = False,
    generator: Generator | None = None,
    corpus_id: str = "contracts-baseline-01",
    api_name: str = "disbursement",
    require_oci_retrieval: bool = False,
) -> dict:
    started = time.perf_counter()
    result = {
        "report_version": "2.0",
        "run_id": str(uuid4()),
        "question": question,
        "status": "insufficient_evidence",
        "versions": [],
        "answer": "",
        "claims": [],
        "citations": [],
        "candidates": [],
        "limitations": [],
        "sufficient_evidence": False,
        "version_filter_pass": None,
        "mode": "oci" if generator else "local",
        "timings_ms": {},
        "semantic_validation": "verbatim_extraction_only",
    }
    stage = "resolve"
    stage_started = started

    def next_stage(name: str) -> None:
        nonlocal stage, stage_started
        now = time.perf_counter()
        result["timings_ms"][stage] = round((now - stage_started) * 1000, 3)
        stage, stage_started = name, now

    try:
        if not isinstance(question, str) or not question.strip() or len(question) > 4000:
            raise ValueError("Question must contain between 1 and 4000 characters")
        if re.search(r"transactions?|operational|metrics?|latency|records?", question, re.I):
            result.update(status="structured_data_required")
            result["limitations"] = [
                "Use an approved read-only query with an explicit time range. "
                "Documentary and operational parts must be answered separately."
            ]
            return result
        versions, status, message = resolve_request(question, version, compare)
        result["versions"] = versions
        if status:
            result.update(status=status, limitations=[message])
            return result
        facets, unsupported = requested_facets(question)
        if not facets and not require_oci_retrieval:
            result["limitations"] = ["No supported contract topic was identified."]
            return result
        next_stage("retrieve")
        candidates = []
        for target in versions:
            items = retriever(target, question)
            if any(
                e.chunk.contract_version != target
                or e.chunk.corpus_id != corpus_id
                or e.chunk.api_name != api_name
                or e.chunk.data_classification != "synthetic"
                for e in items
            ):
                raise ValueError("Retrieval scope validation failed")
            candidates.extend(items)
        result["candidates"] = citations(candidates)
        result["version_filter_pass"] = bool(candidates)
        next_stage("select_evidence")
        evidence, conflict = select_evidence(candidates, facets)
        sources = citations(evidence)
        if conflict:
            result.update(
                status="conflicting_evidence",
                citations=sources,
                limitations=["Conflicting sections require human review."],
            )
            return result
        if not evidence:
            result["limitations"] = ["Insufficient evidence."]
            return result
        covered = {(e.chunk.contract_version, section_facet(e.chunk.section)) for e in evidence}
        missing = {(v, f) for v in versions for f in facets} - covered
        next_stage("generate")
        if generator:
            payload = generator(question, evidence)
        else:
            payload = {
                "status": "answered",
                "claims": [
                    {"text": source["excerpt"], "evidence_ids": [source["evidence_id"]]}
                    for source in sources
                ],
            }
        next_stage("validate_claims")
        if isinstance(payload, dict) and payload.get("provider_usage") is not None:
            result["provider_usage"] = payload["provider_usage"]
        claims = validate_generation(payload, sources)
        if not claims:
            result["limitations"] = ["Insufficient evidence."]
            return result
        used_ids = {eid for claim in claims for eid in claim["evidence_ids"]}
        used_sources = [s for s in sources if s["evidence_id"] in used_ids]
        used_facets = {(s["contract_version"], section_facet(s["section"])) for s in used_sources}
        missing |= {(v, f) for v in versions for f in facets} - used_facets
        result.update(
            status="partial"
            if missing or unsupported or payload["status"] == "partial"
            else "answered",
            claims=claims,
            citations=used_sources,
        )
        result["sufficient_evidence"] = result["status"] == "answered"
        result["answer"] = "\n".join(
            c["text"] + " " + " ".join(f"[{eid}]" for eid in c["evidence_ids"]) for c in claims
        )
        if missing or unsupported:
            result["limitations"] = ["Some requested details are not supported by the evidence."]
    except Exception:
        # Provider exception strings may include credentials, request bodies or identifiers.
        result.update(
            status="error",
            answer="",
            claims=[],
            citations=[],
            sufficient_evidence=False,
            error_stage=stage,
            limitations=["Stage failed. Check the private troubleshooting runbook."],
        )
    finally:
        result["timings_ms"][stage] = round((time.perf_counter() - stage_started) * 1000, 3)
        result["timings_ms"]["total"] = round((time.perf_counter() - started) * 1000, 3)
    return result
