"""Synthetic v1 endpoint used only as a migration baseline."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Synthetic Payments API", version="v1")


class PaymentRequestV1(BaseModel):
    """Version 1 request accepted a client-provided payment status."""

    amount: float = Field(gt=0)
    currency: Literal["CLP"]
    payment_status: Literal["PENDING", "PAID", "FAILED"] = Field(alias="paymentStatus")


@app.post("/payments", status_code=201)
def create_payment(request: PaymentRequestV1) -> dict[str, str]:
    """Return a synthetic result; no payment is executed."""

    return {"status": request.payment_status, "api_version": "v1"}
