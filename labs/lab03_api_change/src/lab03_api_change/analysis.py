"""Deterministic impact analysis for the bounded Lab 3 API migration."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ChangeImpact:
    """One reviewable API-contract impact."""

    change_id: str
    severity: str
    summary: str
    rationale: str
    required_test: str


def analyze_api_change() -> list[ChangeImpact]:
    """Return the approved, bounded impacts of the synthetic v1-to-v2 change."""

    return [
        ChangeImpact(
            change_id="PAY-001",
            severity="high",
            summary="Remove the paymentStatus request field.",
            rationale="A v1 client can no longer supply its own payment state in v2.",
            required_test="A request containing paymentStatus is rejected with HTTP 422.",
        ),
        ChangeImpact(
            change_id="PAY-002",
            severity="high",
            summary="Require the idempotencyKey request field.",
            rationale="Payment-like requests need a stable client key to be safely retried.",
            required_test="A request without idempotencyKey is rejected with HTTP 422.",
        ),
        ChangeImpact(
            change_id="PAY-003",
            severity="medium",
            summary="Return HTTP 202 and a v2 acceptance envelope.",
            rationale=(
                "The endpoint acknowledges processing instead of representing a client-supplied "
                "final status."
            ),
            required_test=(
                "A valid v2 request returns 202, ACCEPTED, a payment_id, and api_version v2."
            ),
        ),
    ]


def impacts_as_dicts() -> list[dict[str, str]]:
    """Convert impacts to JSON-compatible records for the evidence report."""

    return [asdict(impact) for impact in analyze_api_change()]
