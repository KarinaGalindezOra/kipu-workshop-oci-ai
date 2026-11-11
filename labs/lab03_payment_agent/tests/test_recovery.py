"""Offline checks of the bounded, explicitly reviewed recovery exception."""

import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from lab03_payment_agent.recovery import claim_recovery_investigation, reviewed_stopped_runs


@pytest.fixture
def reviewed(tmp_path, monkeypatch):
    settings = SimpleNamespace(
        participant="p002", db_user="WS3_P002", expected_tenancy="tenant", expected_user="user"
    )
    now = datetime.now(UTC)
    issued = now - timedelta(seconds=2)
    run = str(uuid4())
    review = {
        "status": "approved",
        "review_id": str(uuid4()),
        "source_run": run,
        "participant": "p002",
        "db_user": "WS3_P002",
        "expected_tenancy": "tenant",
        "expected_user": "user",
        "approved_at": issued.isoformat(),
        "expires_at": (now + timedelta(minutes=25)).isoformat(),
        "reviewed_stopped_runs": ["one-stopped-native-run"],
        "checks": [
            {
                "checked_at": (issued - timedelta(seconds=n)).isoformat(),
                "run_id": run,
                "reviewed_team_id": "one-stopped-native-run",
                "native_state": "RUNNING",
                "result_characters": 0,
                "active_database_sessions": 0,
                "running_scheduler_jobs": 0,
                "application_locks": 0,
            }
            for n in (2, 1)
        ],
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(review))
    monkeypatch.setenv("LAB03_RECOVERY_REVIEW_FILE", str(path))
    return settings, path, review


def test_recovery_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("LAB03_RECOVERY_REVIEW_FILE", raising=False)
    assert reviewed_stopped_runs(SimpleNamespace()) == frozenset()


def test_review_accepts_only_the_exact_stopped_run_and_claims_once(reviewed):
    settings, _, _ = reviewed
    assert reviewed_stopped_runs(settings) == frozenset({"one-stopped-native-run"})
    claim_recovery_investigation(settings)
    with pytest.raises(ValueError, match="already attempted"):
        claim_recovery_investigation(settings)


@pytest.mark.parametrize(
    "invalid",
    ["proposed", "participant", "expired", "active", "jobs", "locks", "other_run", "same_check"],
)
def test_invalid_or_unverified_reviews_fail_closed(reviewed, invalid):
    settings, path, review = reviewed
    if invalid == "proposed":
        review["status"] = "proposed"
    elif invalid == "participant":
        review["expected_user"] = "another-user"
    elif invalid == "expired":
        review["expires_at"] = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    elif invalid == "active":
        review["checks"][0]["active_database_sessions"] = 1
    elif invalid == "jobs":
        review["checks"][0]["running_scheduler_jobs"] = 1
    elif invalid == "locks":
        review["checks"][0]["application_locks"] = 1
    elif invalid == "other_run":
        review["checks"][0]["reviewed_team_id"] = "different-run"
    else:
        review["checks"][1]["checked_at"] = review["checks"][0]["checked_at"]
    path.write_text(json.dumps(review))
    with pytest.raises(ValueError):
        claim_recovery_investigation(settings)
    assert not list(path.parent.glob("*.attempt-used"))


def test_readonly_review_cannot_claim_a_paid_attempt(reviewed):
    settings, path, review = reviewed
    review["paid_execution_allowed"] = False
    path.write_text(json.dumps(review))
    assert reviewed_stopped_runs(settings) == frozenset({"one-stopped-native-run"})
    with pytest.raises(ValueError, match="read-only"):
        claim_recovery_investigation(settings)
    assert not list(path.parent.glob("*.attempt-used"))


@pytest.mark.parametrize("operation", ["embed", "run"])
def test_readonly_review_blocks_direct_provider_entry_points(reviewed, operation):
    from lab03_payment_agent.domain import Request
    from lab03_payment_agent.live import LiveBackend

    settings, path, review = reviewed
    review["paid_execution_allowed"] = False
    path.write_text(json.dumps(review))
    backend = object.__new__(LiveBackend)
    backend.settings = settings
    with pytest.raises(ValueError, match="read-only"):
        if operation == "embed":
            backend.embed("payment idempotency")
        else:
            backend.run(Request("Investigate payment idempotency.", "PAY-104", "v2"), {}, "run")
