"""Reference implementation of the synthetic Payments API v2."""

from __future__ import annotations

import hashlib
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Synthetic Payments API", version="v2")


class PaymentRequestV2(BaseModel):
    """Accepted v2 input; unknown legacy fields fail closed."""

    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    currency: Literal["CLP"]
    idempotency_key: str = Field(alias="idempotencyKey", min_length=8, max_length=64)


class PaymentResponseV2(BaseModel):
    """Synthetic acceptance result; this lab never executes a payment."""

    payment_id: str
    status: Literal["ACCEPTED"]
    api_version: Literal["v2"]


def payment_id_for(idempotency_key: str) -> str:
    """Create a deterministic synthetic identifier from the supplied client key."""

    digest = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()[:12]
    return f"pay_{digest}"


@app.post("/payments", status_code=202, response_model=PaymentResponseV2)
def create_payment(request: PaymentRequestV2) -> PaymentResponseV2:
    """Accept a syntactically valid v2 request without executing any payment."""

    return PaymentResponseV2(
        payment_id=payment_id_for(request.idempotency_key),
        status="ACCEPTED",
        api_version="v2",
    )
