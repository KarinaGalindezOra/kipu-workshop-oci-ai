# Disbursement API Contract v1

Contract Version: v1

## Status update endpoint

Clients update a disbursement with `PATCH /v1/disbursements/{disbursement_id}`. The request body uses `payment_status` with one of `PENDING`, `PAID`, or `FAILED`.

## Idempotency

Every status update must include the `X-Idempotency-Key` header. Reusing a key with a different request body returns `409 IDEMPOTENCY_CONFLICT`.

## Response

A successful status update returns `200 OK` with `disbursement_id`, `payment_status`, and `updated_at`.

## Error handling

An unknown disbursement returns `404 DISBURSEMENT_NOT_FOUND`. An invalid status returns `422 INVALID_PAYMENT_STATUS`.
