# Lab 3 Facilitator Guide

## Outcome

Participants use a small synthetic FastAPI API change to distinguish AI-generated engineering suggestions from a safe, reviewable, and testable implementation.

## Duration

| Segment | Minutes | Evidence |
| --- | ---: | --- |
| Introduce the v1 and v2 contracts | 15 | The team can explain the breaking changes. |
| Explain the AI-assisted change workflow | 15 | Participants know that the model proposes and engineers decide. |
| Generate and review an impact plan | 25 | The plan identifies removed, added, and changed behavior. |
| Review and apply the bounded patch | 35 | The patch changes only the synthetic API scope. |
| Execute regression tests | 30 | Valid v2 and rejected v1 requests are proven. |
| Challenge failure cases and close | 20 | Participants identify missing idempotency and legacy-field failures. |

This 140-minute core leaves approximately 40 minutes within a three-hour slot for setup, questions, and contingency.

## Preparation

1. Confirm each team has Python 3.11.9 and the repository dependencies installed.
2. Run `python -m pytest labs/lab03_api_change/tests` once before the session.
3. If using the OCI chat segment, confirm the tenant has an approved model and that participants know the synthetic-data rule.
4. Do not grant source-control write access, production API access, or deployment privileges for this lab.

## Facilitation sequence

1. Show the v1 endpoint and ask what could break if `paymentStatus` disappears.
2. Show the v2 specification. Ask why idempotency belongs to the request contract for payment-like operations.
3. Use the prompt template to obtain a draft plan from an approved OCI chat model, or use the deterministic report if the model is unavailable.
4. Compare the draft with the expected impact report. Reject unsupported claims and out-of-scope changes.
5. Inspect the patch line by line. Explain that it rejects extra fields so clients do not silently assume the old contract still works.
6. Run the tests and discuss the negative tests as evidence of a controlled API change.

## Guardrails

- Use only the supplied synthetic source and contract.
- Do not paste Khipu repositories, secrets, source-control tokens, database connection data, or customer data into a model prompt.
- Do not allow a model to commit, deploy, call APIs, or approve its own patch.
- Keep the scope to one endpoint; this is an engineering-control demonstration, not autonomous coding.

## Evidence gate

- [ ] `PAY-001`, `PAY-002`, and `PAY-003` are present in the impact report.
- [ ] The patch requires `idempotencyKey` and rejects `paymentStatus`.
- [ ] The valid v2 request returns `202` and `ACCEPTED`.
- [ ] The legacy v1 payload returns a validation error.
- [ ] All Lab 3 tests pass.
- [ ] Only synthetic material was used.
