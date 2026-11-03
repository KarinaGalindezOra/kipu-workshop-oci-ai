# Disbursement API Contract v2

Contract Version: v2

## Settlement status endpoint

Clients update settlement status with `PUT /v2/disbursements/{disbursement_id}/status`. The request body uses `status` with one of `PROCESSING`, `SETTLED`, or `REJECTED`.

## Idempotency

Every status update must include the `Idempotency-Key` header. Reusing a key with a different request body returns `409 IDEMPOTENCY_MISMATCH`.

## Response

A successful status update returns `200 OK` with `disbursement_id`, `status`, `status_changed_at`, and `contract_version` equal to `v2`.

## Migration from v1

The v1 endpoint and field `payment_status` are not accepted by v2. Clients must call the v2 settlement status endpoint, rename `payment_status` to `status`, and map `PAID` to `SETTLED`, `PENDING` to `PROCESSING`, and `FAILED` to `REJECTED`.

## Error handling

An unknown disbursement returns `404 DISBURSEMENT_NOT_FOUND`. An invalid status returns `422 INVALID_STATUS`.
