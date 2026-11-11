# Synthetic Payments Contract — v2

This document is a synthetic workshop fixture, not a commercial payment agreement.

## Idempotency: different-payload

A repeated idempotency key with a different payload must be rejected. Preserve the original request identifier and escalate for investigation.

## Idempotency: same-payload

A repeated key with the same payload refers to the original request and must not create another payment.

## Traceability: original-request

Preserve the original request identifier when reporting an idempotency conflict. Include the identifiers of the related requests in the investigation case.

## Evidence: payload-evidence

Compare the payload hashes of requests that share an idempotency key. A claim that the payload changed requires different observed payload hashes.

## Evidence: event-evidence

Consult the payment events before preparing an investigation recommendation. A contractual clause does not establish that a payment event occurred.

## Missing evidence: missing-payment

If the requested payment is not found, report insufficient operational evidence. Do not invent payment events or related requests.

## Human review: human-review

A human reviewer must approve the exact case before registration. An investigation recommendation does not authorize a payment or a refund.

## Memory governance: memory-authority

An approved procedural memory may guide an investigation. The current contract takes precedence over an incompatible memory, and a memory does not grant permissions.

## Memory governance: lesson-approval

Registering an investigation case does not approve a new procedural memory. A reusable lesson requires a separate human review of its content, contract version and source execution.
