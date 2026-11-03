"""Regression tests for the synthetic Payments API v2."""

from fastapi.testclient import TestClient
from lab03_api_change.app import app, payment_id_for

client = TestClient(app)


def test_valid_v2_request_is_accepted() -> None:
    response = client.post(
        "/payments",
        json={"amount": 12500, "currency": "CLP", "idempotencyKey": "team01-demo-key"},
    )

    assert response.status_code == 202
    assert response.json() == {
        "payment_id": payment_id_for("team01-demo-key"),
        "status": "ACCEPTED",
        "api_version": "v2",
    }


def test_request_without_idempotency_key_is_rejected() -> None:
    response = client.post("/payments", json={"amount": 12500, "currency": "CLP"})

    assert response.status_code == 422


def test_legacy_payment_status_field_is_rejected() -> None:
    response = client.post(
        "/payments",
        json={
            "amount": 12500,
            "currency": "CLP",
            "idempotencyKey": "team01-demo-key",
            "paymentStatus": "PAID",
        },
    )

    assert response.status_code == 422
