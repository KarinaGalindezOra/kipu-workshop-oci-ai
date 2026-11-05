"""Evidence selection for the deliberately bounded contract workshop domain."""

import hashlib
import re
from dataclasses import asdict

from .models import RetrievedEvidence

FACETS = {
    "migration": r"migr|moving|map\b|mape|mapping|rename|renombr|payment_status.*(?:v1 endpoint|endpoint de v1)",
    "idempotency": r"idempoten|header|encabezado|409|conflict|mismatch",
    "response": r"timestamp|response|respuesta|returns?\b|successful|exitosa|status_changed_at|updated_at",
    "errors": r"error|invalid|inválid|unknown disbursement|desembolso desconocido|404|422",
    "endpoint": r"endpoint|method|método|request body|cuerpo de solicitud|allowed|permitidos|states|estados|values|valores|fields|campos|update|actualiz|status\b|estado\b",
}
UNSUPPORTED = re.compile(
    r"\bsla\b|availability|disponibilidad|certificate|certificado|\btls\b|authentication|autenticación|oauth|rate limit|"
    r"accounting|contabilidad|business meaning|significado empresarial|retention|retención|encryption|cifrado|rotation|rotación|guarantee|garantía",
    re.I,
)


def requested_facets(question: str) -> tuple[set[str], bool]:
    facets = {name for name, pattern in FACETS.items() if re.search(pattern, question, re.I)}
    # Specific questions should not acquire a generic endpoint requirement from 'status'.
    if facets - {"endpoint"} and not re.search(
        r"endpoint|method|método|request body|cuerpo de solicitud|fields|campos", question, re.I
    ):
        facets.discard("endpoint")
    return facets, bool(UNSUPPORTED.search(question))


def section_facet(section: str) -> str | None:
    name = section.lower()
    if "migration" in name or "migración" in name:
        return "migration"
    if "idempotency" in name or "idempotencia" in name:
        return "idempotency"
    if "response" in name or "respuesta" in name:
        return "response"
    if "error" in name:
        return "errors"
    if "endpoint" in name or name in {"status", "estado"}:
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
                    f"{chunk.section} | líneas {chunk.line_start}–{chunk.line_end}"
                ),
            }
        )
    return result
