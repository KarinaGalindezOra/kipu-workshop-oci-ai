"""Bounded operator review of stopped native history; never a database permission grant."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID


def load_review(settings):
    """Read only an explicitly configured server-side operator review, never prompt text.

    This local safety record is not an authentication boundary. The facilitator must
    independently inspect server activity before issuing it. Database grants and
    authenticated participant identity remain unchanged.
    """
    name = os.environ.get("LAB03_RECOVERY_REVIEW_FILE")
    if not name:
        return None
    path = Path(name).resolve()
    if path.is_relative_to(Path(__file__).resolve().parents[4]):
        raise ValueError("Recovery review must remain outside the repository")
    review = json.loads(path.read_text(encoding="utf-8"))
    if review.get("status") != "approved":
        raise ValueError("Recovery review requires explicit operator approval")
    now = datetime.now(UTC)
    issued = datetime.fromisoformat(review["approved_at"])
    expires = datetime.fromisoformat(review["expires_at"])
    if (
        review.get("status") != "approved"
        or review.get("participant") != settings.participant
        or review.get("db_user") != settings.db_user
        or review.get("expected_tenancy") != settings.expected_tenancy
        or review.get("expected_user") != settings.expected_user
        or issued.tzinfo is None
        or expires.tzinfo is None
        or not issued <= now < expires
        or not 0 < (expires - issued).total_seconds() <= 1800
    ):
        raise ValueError("Recovery review is expired or does not match the assignment")
    UUID(review["review_id"])
    UUID(review["source_run"])
    identifiers = review.get("reviewed_stopped_runs", [])
    if len(identifiers) != 1 or not isinstance(identifiers[0], str) or not identifiers[0]:
        raise ValueError("Recovery review must identify exactly one stopped native run")
    checks = review.get("checks", [])
    if len(checks) != 2:
        raise ValueError("Two independent server checks are required")
    for check in checks:
        checked = datetime.fromisoformat(check["checked_at"])
        if (
            checked.tzinfo is None
            or not 0 <= (issued - checked).total_seconds() <= 600
            or check.get("run_id") != review["source_run"]
            or check.get("reviewed_team_id") != identifiers[0]
            or check.get("native_state") != "RUNNING"
            or check.get("result_characters") != 0
            or any(
                type(check.get(key)) is not int or check[key] != 0
                for key in (
                    "active_database_sessions",
                    "running_scheduler_jobs",
                    "application_locks",
                )
            )
        ):
            raise ValueError("Server activity was not verified stopped for this exact run")
    if checks[0]["checked_at"] == checks[1]["checked_at"]:
        raise ValueError("Server checks must be separate observations")
    return path, review


def reviewed_stopped_runs(settings):
    loaded = load_review(settings)
    return frozenset(loaded[1]["reviewed_stopped_runs"]) if loaded else frozenset()


def ensure_paid_execution_allowed(settings):
    loaded = load_review(settings)
    if loaded and loaded[1].get("paid_execution_allowed") is False:
        raise ValueError("Recovery review is read-only; no new paid execution is authorized")
    return loaded


def claim_recovery_investigation(settings):
    """Consume the recovery's single paid-attempt slot before embedding, including failures."""
    loaded = ensure_paid_execution_allowed(settings)
    if loaded:
        path, review = loaded
        marker = path.parent / (review["review_id"] + ".attempt-used")
        try:
            with marker.open("x", encoding="utf-8") as stream:
                stream.write(review["review_id"])
        except FileExistsError:
            raise ValueError(
                "The single approved recovery investigation was already attempted"
            ) from None
