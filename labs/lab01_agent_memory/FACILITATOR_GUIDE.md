# Lab 1 Facilitator Guide

The authoritative Spanish delivery runbook is [docs/facilitator-guides/01-decision-memory.md](../../docs/facilitator-guides/01-decision-memory.md).

## Non-negotiable controls

- One disposable OCI trial per team; retain the current facilitator trial for rehearsal.
- One ADB and one Agent Memory store per team trial.
- One memory owner and one temporary application database user per participant.
- The owner provisions the official Agent Memory package and initializes the store once with `SchemaPolicy.CREATE_IF_NECESSARY`.
- Participants execute the SDK with `SchemaPolicy.REQUIRE_EXISTING`.
- Wallets and passwords are delivered through an approved private channel and never kept in source, Terraform state, dashboard uploads, or shared archives.
- The workshop uses only repository synthetic data.

## Go / no-go signal

An application user must complete the direct SDK run before the session and produce:

```text
LAB01_OCI_SDK_READY
SCHEMA_POLICY REQUIRE_EXISTING
PERSISTENCE_CONFIRMED True
ISOLATION_PASS True
```

The local FastAPI gateway remains a teaching example for authenticated-scope derivation. It is not the Lab 1 participant execution path.
