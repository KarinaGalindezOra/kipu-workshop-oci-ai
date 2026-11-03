# Payments API v2 - Approved Synthetic Contract

## POST /payments

### Request body

The JSON request body must include:

- `amount`: positive number.
- `currency`: the literal value `CLP`.
- `idempotencyKey`: non-empty string from 8 to 64 characters.

`paymentStatus` is not part of version 2. Unknown request fields are rejected.

### Response

On acceptance, the endpoint returns HTTP `202` with:

```json
{
  "payment_id": "pay_<deterministic-id>",
  "status": "ACCEPTED",
  "api_version": "v2"
}
```

The endpoint accepts a request for processing. It does not execute a payment in this laboratory.
