"""Tests for the team-scoped local deployment gateway."""

from fastapi.testclient import TestClient
from lab01_agent_memory.deployment_api import LocalMemoryRepository, create_app
from lab01_agent_memory.gateway_auth import issue_local_team_token

TOKEN_SECRET = "local-rehearsal-secret-only"


def _headers(team_id: str) -> dict[str, str]:
    return {
        "X-Workshop-Token": issue_local_team_token(
            team_id,
            TOKEN_SECRET,
            ttl_seconds=600,
        )
    }


def _bundle(team_id: str, procedure_id: str, content: str, tags: list[str]) -> dict[str, object]:
    return {
        "team_id": team_id,
        "display_name": team_id,
        "procedures": [{"id": procedure_id, "content": content, "tags": tags}],
    }


def test_gateway_derives_scope_from_token_and_blocks_cross_team_retrieval() -> None:
    client = TestClient(create_app(TOKEN_SECRET, LocalMemoryRepository()))

    payments_deploy = client.post(
        "/v1/bundles/deploy",
        headers=_headers("team-payments"),
        json=_bundle(
            "team-payments",
            "payment-idempotency",
            "Reject repeated payment requests using their idempotency key.",
            ["payment", "idempotency"],
        ),
    )
    integrations_deploy = client.post(
        "/v1/bundles/deploy",
        headers=_headers("team-integrations"),
        json=_bundle(
            "team-integrations",
            "migration-rollout",
            "Run database migration in controlled phases with a rollback checkpoint.",
            ["database", "migration"],
        ),
    )

    assert payments_deploy.status_code == 200
    assert integrations_deploy.status_code == 200

    cross_team_query = client.post(
        "/v1/memory/query",
        headers=_headers("team-payments"),
        json={"query": "database migration controlled phases"},
    )

    assert cross_team_query.status_code == 200
    assert cross_team_query.json()["authenticated_team_id"] == "team-payments"
    assert cross_team_query.json()["procedure_ids"] == []


def test_gateway_rejects_bundle_when_claimed_team_differs_from_authenticated_team() -> None:
    client = TestClient(create_app(TOKEN_SECRET, LocalMemoryRepository()))

    response = client.post(
        "/v1/bundles/deploy",
        headers=_headers("team-payments"),
        json=_bundle(
            "team-integrations",
            "migration-rollout",
            "Run database migration in controlled phases with a rollback checkpoint.",
            ["database", "migration"],
        ),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "The bundle is not authorized for this team"
