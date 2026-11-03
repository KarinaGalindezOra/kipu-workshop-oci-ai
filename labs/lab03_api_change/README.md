# Lab 3: API Change Analysis, Patch, and Regression Tests

## Goal

Show how an AI-assisted engineering workflow can turn a small, explicit API-contract change into a reviewable patch and executable regression tests.

## Workshop message

OCI turns technical context into safer, testable changes.

## Scenario

The synthetic Payments API evolves from v1 to v2. Version 2 removes `paymentStatus`, requires `idempotencyKey`, returns `202 Accepted`, and provides an explicit `api_version` in the response.

The exercise is intentionally bounded. It does not execute payments, call external systems, or use Khipu code or data.

## What participants produce

- A structured impact analysis for the v1-to-v2 change.
- A reviewable unified patch.
- Regression tests that prove the v2 API accepts the new request and rejects the legacy contract.
- An evidence report that can be checked before code is proposed for merge.

## Run the deterministic workshop path

Install the Lab 3 dependencies once from the repository root:

```powershell
python -m pip install -e ".[dev,lab01,lab03]"
```

Generate the analysis and patch evidence:

```powershell
python -m lab03_api_change.demo --output-dir artifacts/lab03/team-01
python -m pytest labs/lab03_api_change/tests
```

The evidence files are written to `artifacts/lab03/team-01`. They are generated outputs and must not be committed.

## Participant workflow

1. Read the v1 endpoint in [exercise/payment_api_v1.py](exercise/payment_api_v1.py).
2. Read the approved v2 specification in [data/payment_api_v2.md](data/payment_api_v2.md).
3. Use [prompts/change-analysis.md](prompts/change-analysis.md) with an approved OCI Generative AI chat model to draft a change plan. The model proposes; the team reviews.
4. Compare the plan against the deterministic analysis report and review [patches/payment_api_v2.patch](patches/payment_api_v2.patch).
5. Run the regression tests. A patch is not accepted merely because it looks plausible.

## OCI-assisted path

The live segment uses OCI Generative AI Inference only as an engineering assistant. Send the synthetic v1 source and v2 specification, not credentials, wallets, production source code, customer information, or proprietary Khipu contracts.

The deterministic analyzer and tests remain the acceptance gate. The LLM output is treated as an untrusted draft that must be reviewed and tested.

## Acceptance criteria

- The analysis identifies the removed field and new required idempotency field.
- The patch uses `idempotencyKey` in the JSON request and rejects unexpected legacy fields.
- A valid v2 request returns `202` and `ACCEPTED`.
- A legacy request fails validation.
- Regression tests pass without OCI access.
