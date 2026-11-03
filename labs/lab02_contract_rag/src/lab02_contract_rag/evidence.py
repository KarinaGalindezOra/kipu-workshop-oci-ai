"""Evidence selection for the deliberately bounded contract workshop domain."""

import hashlib
import re
from dataclasses import asdict

from .models import RetrievedEvidence

FACETS = {
    "migration": r"migrat|moving|map\b|mapping|rename|payment_status.*v1 endpoint",
    "idempotency": r"idempoten|header|409|conflict|mismatch",
    "response": r"timestamp|response|returns?\b|successful|status_changed_at|updated_at",
    "errors": r"error|invalid|unknown disbursement|404|422",
    "endpoint": r"endpoint|method|request body|allowed|states|values|fields|update|status\b",
}
UNSUPPORTED = re.compile(
    r"\bsla\b|availability|certificate|\btls\b|authentication|oauth|rate limit|"
    r"accounting|business meaning|retention|encryption|rotation|guarantee",
    re.I,
)


def requested_facets(question: str) -> tuple[set[str], bool]:
    facets = {name for name, pattern in FACETS.items() if re.search(pattern, question, re.I)}
    # Specific questions should not acquire a generic endpoint requirement from 'status'.
    if facets - {"endpoint"} and not re.search(
        r"endpoint|method|request body|fields", question, re.I
    ):
        facets.discard("endpoint")
    if "migration" in facets:
        facets.add("endpoint")
    return facets, bool(UNSUPPORTED.search(question))


def section_facet(section: str) -> str | None:
    name = section.lower()
    if "migration" in name:
        return "migration"
    if "idempotency" in name:
        return "idempotency"
    if "response" in name:
        return "response"
    if "error" in name:
        return "errors"
    if "endpoint" in name or name == "status":
        return "endpoint"
    return None


def select_evidence(candidates: list[RetrievedEvidence], facets: set[str]):
    selected = [e for e in candidates if section_facet(e.chunk.section) in facets]
    for item in selected:
        if hashlib.sha256(item.chunk.content.encode()).hexdigest() != item.chunk.content_hash:
            raise ValueError("Evidence integrity validation failed")
        if re.search(r"ignore.*instruction|reveal.*secret|system prompt", item.chunk.content, re.I):
            raise ValueError("Untrusted instruction detected in evidence")
    seen: dict[tuple[str, str], str] = {}
    conflict = False
    for item in selected:
        key = (item.chunk.contract_version, item.chunk.section)
        if key in seen and seen[key] != item.chunk.content_hash:
            conflict = True
        seen[key] = item.chunk.content_hash
    return selected, conflict


def citations(evidence: list[RetrievedEvidence]) -> list[dict]:
    result = []
    for index, item in enumerate(evidence, 1):
        chunk = item.chunk
        metadata = asdict(chunk)
        for name in ("embedding", "embedding_model_id", "embedding_dimension"):
            metadata.pop(name, None)
        result.append(
            {
                **metadata,
                "evidence_id": f"E{index}",
                "excerpt": chunk.content,
                "method": item.method,
                "rank_value": item.score,
                "score_type": item.score_type,
                "label": (
                    f"E{index} — {chunk.source_title} | {chunk.contract_version} | "
                    f"{chunk.section} | lines {chunk.line_start}–{chunk.line_end}"
                ),
            }
        )
    return result
