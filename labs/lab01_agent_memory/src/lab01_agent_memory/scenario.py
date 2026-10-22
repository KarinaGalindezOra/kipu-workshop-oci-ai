"""Synthetic engineering scenario shared by the Lab 1 demo and tests."""

from .models import Guideline


GUIDELINES = [
    Guideline(
        identifier="payment-idempotency",
        content=(
            "For payment operations, require an idempotency key, preserve the original request "
            "identifier, and reject a second request with a mismatched payload."
        ),
        tags=("payments", "idempotency", "api"),
    ),
    Guideline(
        identifier="contract-versioning",
        content=(
            "When a request references multiple API contract versions, prefer the highest approved "
            "version and return the source version used as evidence."
        ),
        tags=("contracts", "versioning", "api"),
    ),
    Guideline(
        identifier="audit-traceability",
        content=(
            "Every integration decision must preserve a correlation identifier, source system, and "
            "timestamp for audit review."
        ),
        tags=("audit", "traceability", "integration"),
    ),
]


def baseline_prompt(question: str) -> str:
    """Return the repeated prompt used as the no-memory baseline."""

    instructions = "\n".join(f"- {guideline.content}" for guideline in GUIDELINES)
    return (
        "You are an integration engineering assistant. Always follow every engineering rule below.\n"
        f"{instructions}\n\n"
        f"User question: {question}"
    )


def compact_prompt(question: str) -> str:
    """Return the request used when the relevant guidelines are retrieved separately."""

    return (
        "You are an integration engineering assistant. Use only the retrieved team-scoped guidelines "
        f"as engineering context.\n\nUser question: {question}"
    )
