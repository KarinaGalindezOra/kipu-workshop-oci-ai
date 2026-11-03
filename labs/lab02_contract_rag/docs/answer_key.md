# Facilitator answer key

The real-workshop reference is data/evaluation/workshop_questions.json (16 cases). The older acceptance_questions.json includes developer-only artificial fixtures and must not be presented as real execution. Baseline source locators:

| Version | Section | Lines | Required facts |
|---|---|---|---|
| v1 | Status update endpoint | 5-7 | PATCH /v1/disbursements/{disbursement_id}; payment_status; PENDING/PAID/FAILED |
| v1 | Idempotency | 9-11 | X-Idempotency-Key; 409 IDEMPOTENCY_CONFLICT |
| v1 | Response | 13-15 | 200 OK; disbursement_id/payment_status/updated_at |
| v1 | Error handling | 17-19 | 404 DISBURSEMENT_NOT_FOUND; 422 INVALID_PAYMENT_STATUS |
| v2 | Settlement status endpoint | 5-7 | PUT /v2/disbursements/{disbursement_id}/status; status; PROCESSING/SETTLED/REJECTED |
| v2 | Idempotency | 9-11 | Idempotency-Key; 409 IDEMPOTENCY_MISMATCH |
| v2 | Response | 13-15 | 200 OK; disbursement_id/status/status_changed_at/contract_version=v2 |
| v2 | Migration from v1 | 17-19 | Old endpoint/payment_status not accepted; PAID→SETTLED; PENDING→PROCESSING; FAILED→REJECTED |
| v2 | Error handling | 21-23 | 404 DISBURSEMENT_NOT_FOUND; 422 INVALID_STATUS |

T01/T02: v1 endpoint. T03: v2 endpoint. T04: v2 idempotency. T05/T15: clarify version. T06/T09/T14: v2 migration plus endpoint. T07: v2 response. T08: both idempotency sections from separate retrievals. T10/T11: insufficient evidence. T12: structured_data_required. T13: v2 errors. T19: unsupported v3 without fallback. T16/T17/T18/T20 remain developer-only tests and are excluded from the participant dashboard and OCI acceptance.

No baseline section specifies availability SLA, TLS rotation, authentication, rate limits, accounting meaning or live transaction counts. Do not infer them. A migration answer need not use v1 evidence when v2 explicitly documents the mapping; a header comparison does require both versions.
