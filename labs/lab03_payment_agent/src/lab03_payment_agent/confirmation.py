"""Content-bound confirmations and durable idempotency, without model authority."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from .domain import LEARNED_RULE, Result, digest


class Repository(Protocol):
    def put_once(self, key: str, kind: str, payload: dict) -> dict: ...


@dataclass(frozen=True)
class Review:
    identity: str
    kind: str
    payload_hash: str


def review(identity: str, kind: str, payload: dict) -> Review:
    if kind not in {"case", "memory"}:
        raise ValueError("Unknown confirmation kind")
    return Review(identity, kind, digest(payload))


def save(
    repository: Repository, identity: str, kind: str, payload: dict, approved: Review | None
) -> dict:
    if approved != review(identity, kind, payload):
        raise ValueError("Explicit confirmation of this exact content is required")
    key = digest(asdict(approved))
    return repository.put_once(key, kind, payload)


def memory_proposal(result: Result) -> dict:
    if result.status != "answered" or not result.proposal:
        raise ValueError("A validated escalation is required")
    return {
        "identifier": "payment-idempotency-approved",
        "content": LEARNED_RULE,
        "version": "v2",
        "source_run": result.run_id,
        "approved": True,
    }
