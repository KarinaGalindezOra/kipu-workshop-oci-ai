# Chicago readiness for 15 concurrent participants

Target: 15 people executing independently, one shared tenancy, compartment and ADB, individual OCI identities and KHIPU_L2_P001 through KHIPU_L2_P015 schemas. One local dashboard process per person. This target is not a claim that the current tenancy has passed a load test.

## Preflight gates

- Confirm tenant readiness, subscribed Chicago region, approved embedding/chat model availability, model request format and vector dimension.
- Approve budget and service access before inference. Trial is optional: a suitable existing nonproduction tenancy can be used. Do not assume trial credits or Always Free capacity cover the complete exercise.
- Prepare 15 individual identities/profiles, 15 database users/schemas and own vector tables; no shared participant credentials. Validate identity mapping, own table and peer denial before handoff.
- Validate protected local dashboard access on all 15 workstations, virtual environments, private wallet paths and calibrated configuration.
- Confirm the shared ADB service can handle at least 15 active participant connections plus facilitator/administrative overhead and query capacity. Do not infer actual throughput from the number of schemas alone.
- Test all 15 performing query embedding/retrieval/chat concurrently with approved credentials. Use real requests, record per-person run IDs and service traces, median/p95 time, errors, throttling and provider usage. No synthetic response delays or fake provider results can pass this gate.
- Coordinate approved waves if throttling occurs. Do not add silent retries, dedicated clusters or resize ADB without cost review and explicit approval.

## Request budget bridge

The baseline has nine document chunks. A full first load across 15 participants stores 135 chunk vectors and normally uses 15 document-embedding batch requests if each participant sends the nine chunks once. Repeated unchanged loads reuse stored vectors; counts depend on actual failures and retries.

The 16-case workshop matrix has 10 positive documentary cases, 2 unsupported documentary retrieval cases and 4 application-control cases. Under the expected successful path this is 12 query-embedding calls and 10 chat calls per participant, or 180 query embeddings and 150 chat requests across 15 participants. The comparison case shares one query embedding between two filtered vector searches. Custom questions, reruns, development calibration and ingestion add consumption. Generation may be skipped when retrieval fails; a partial/failed attempt is not free merely because the UI lacks a completed answer.

These are request counts, not prices, token estimates or guaranteed completions. Record actual provider usage and selected model pricing during approval. The current developer tests do not measure OCI latency, quotas or cost.

## Failure handling

OCI on-demand throttling can change dynamically. A single static request-per-minute number is not a capacity guarantee. The runner disables automatic provider retries and surfaces a failed rate-limited operation; the facilitator spaces a separately authorized retry or adjusts the schedule. Preserve the failure report and do not replace it with a local answer.

When an operational error occurs, stop the participant's batch to avoid account lockout or repeated paid failures. Resume only after checking the cause privately. Shared ADB stop/start and cleanup windows must account for all 15 participants.

## Sign-off

Record participant count, rehearsal time, model/configuration revision, observed limits, budget owner, network approver and facilitator decision. Require real 16-case evidence plus the human rubric from each participant. No go-live status can be inferred from unit tests or dashboard screenshots.

Reference: [OCI on-demand mode and dynamic throttling](https://docs.oracle.com/en-us/iaas/Content/generative-ai/modes.htm).
