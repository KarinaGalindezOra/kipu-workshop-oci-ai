# Lab 2: real OCI contract RAG with visible answers and evidence

Workshop 2 runs for 180 minutes with **15 participants**, each using a local dashboard and an individual OCI/database identity. One Chicago tenancy and one Autonomous AI Database are shared. No tenant or ADB per person is required. The actual tenancy, models, quota and budget must pass preflight; capacity for 15 concurrent participants is a rehearsal target, not an already verified result.

## What the participant sees

The local Streamlit dashboard executes actual OCI operations. It displays the question, observed answer, expected answer criteria, automated checks, limitations, claims, source excerpts, version/section/lines, candidate ranks, service-operation outcomes, latency and provider usage when available. There is no simulator, canned model output, report upload or participant selector. Only the assigned participant's real-workflow reports can be opened.

The approved corpus remains synthetic disbursement contracts v1/v2, four and five sections respectively. Synthetic **data** is intentional; simulated **execution** is excluded from the workshop. Source files and reference criteria never substitute for OCI responses.

## Setup and launch

Use Python 3.11.9 in the project virtual environment. From the source checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,lab02,ui]"
```

Participants on macOS or Linux use the single Python-based route in the [macOS and Linux participant guide](docs/macos_linux_participant_guide.md). It loads a private dotenv session file with `--session-file`; no shell sourcing, passwords, tokens, or private keys are permitted in that file. The existing PowerShell launchers remain a Windows administrator compatibility path.

Load your completed private session file based on config/participant-session.ps1.example. LAB02_PARTICIPANT_ID is mandatory: p001 maps to KHIPU_L2_P001, through p015 for this event. Each person must have their own OCI profile, database login, wallet access and private workspace. No administrator/shared database credentials are accepted.

```powershell
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
python labs/lab02_contract_rag/scripts/run_dashboard.py
```

Open [the local dashboard](http://127.0.0.1:8502). The launcher binds only to 127.0.0.1. Each person uses their own workstation or an approved private environment. Do not expose the dashboard publicly or use it as a shared authenticated service. Private Cloud Shell access/port preview needs separate networking review.

Opening the dashboard does not invoke OCI. Each execution requires an unchecked-by-default paid-inference acknowledgement. The first ADB request in a local dashboard session requires private password entry; later requests may reuse one participant-only, one-connection local pool while the dashboard process remains open. Loading missing chunks requires an additional acknowledgement. Password fields reset on submission; plaintext credentials are never cached or stored in reports. Organization/budget approval remains required in addition to UI checkboxes.

## Real workshop sequence

1. Inspect the two source contracts and nine chunks. Local Python parsing is real preprocessing, not a replacement retrieval engine.
2. In the dashboard choose **Prepare my synthetic corpus**. After approved inference/load acknowledgements, OCI generates document embeddings and ADB inserts missing chunks in your own schema. No DDL is run by the dashboard.
3. The facilitator freezes development calibration for the approved corpus/model/region/dimension. Set LAB02_CALIBRATION_FILE privately. A common compatible calibration may be distributed; mutable vector tables remain individual.
4. Choose a predefined question and **Ask using OCI**. The actual SDK embeds the question, ADB performs version-filtered exact vector search, and OCI chat selects supported claims. Read the observed answer beside its expected criteria and expand the evidence.
5. Test version comparison, a missing version and unsupported documentation. Review the recorded operation trace: clarification/routing are application decisions, not model answers. Unsupported documentary questions with a valid version perform real OCI retrieval; if no supporting evidence is selected, chat is skipped and this is visible.
6. Inspect your own execution history and submit the individual rubric.

The model receives the question and retrieved evidence, never the reference answer. Claims are verbatim source sentences/excerpts under the current MVP. Invalid IDs, unsupported paraphrases or provider failures produce an error; no lexical/local answer is substituted. Custom questions have no invented reference answer: citation inspection remains available and human correctness review is required.

## Reference cases and acceptance

`data/evaluation/workshop_questions.json` contains **16 real-workflow scenarios** with expected states, source sections, required facts and a human-readable reference. Ten are positive documentary cases, two test unsupported documentation after real retrieval, and four test application clarification/routing/unsupported-version decisions. Not every scenario should call a model: the trace accurately distinguishes control decisions from service calls.

Automated checks validate state, citation references, source hashes, expected source sections, version scope and required facts. A pass does not certify semantic relevance/completeness; read the actual answer and sources. A system that always abstains fails positive cases. The UI shows failures alongside the actual outcome.

After budget approval, the same real execution path is available through the CLI:

```powershell
python labs/lab02_contract_rag/scripts/run_live_validation.py --question "In v2, what idempotency header is required?" --confirm-live-inference
python labs/lab02_contract_rag/scripts/evaluate.py --confirm-live-inference
```

For explicitly approved loading, add --confirm-synthetic-load. The evaluator stops on an operational error to avoid repeated failed logins/paid retries and marks remaining cases not run. Its cloud acceptance requires all 16 cases, plus independent human review. It cannot select an offline mode.

## Administrator preparation

Use [participant isolation](docs/participant_isolation.md), [dashboard operations](docs/dashboard_operations.md) and the [15-participant readiness checklist](docs/capacity_15.md). Shared infrastructure and per-person schema/table creation require separate approval. The dashboard never provisions users, IAM, networks or databases.

Before onboarding the remaining participants, the facilitator performs the real [p001 end-to-end rehearsal](docs/p001_end_to_end_rehearsal.md). It is the canonical guided route for validating the dashboard, OCI evidence flow and negative behaviours without claiming 15-person concurrency readiness.

The new v2 table schema is incompatible with legacy tables: prepare a separate approved schema/table rather than overwriting a previous exercise. Check own-schema access and bidirectional read denial against two administrator-confirmed existing participant tables before the event.

For approved ingestion and calibration preparation:

```powershell
python labs/lab02_contract_rag/scripts/validate_environment.py --confirm-synthetic-external-inference
python labs/lab02_contract_rag/scripts/ingest_oci.py --confirm-live-inference --confirm-synthetic-load
python labs/lab02_contract_rag/scripts/collect_calibration.py --confirm-live-inference --output labs/lab02_contract_rag/config/private/development-distances.json
python labs/lab02_contract_rag/scripts/calibrate.py --measurements labs/lab02_contract_rag/config/private/development-distances.json --output labs/lab02_contract_rag/config/private/calibration.json
```

Never calibrate on acceptance cases. Calibration preserves recall for labeled positive development evidence; if positive/negative candidate distances overlap, the private calibration records that risk and evidence selection remains mandatory. Distance is never proof of contractual support. Model family/dimension compatibility and Chicago availability must be verified in the actual tenancy. Configurable embedding output dimensions are optional and enabled only for supported models. The chat adapter uses the OCI `GenericChatRequest` format; the approved default is xAI Grok 4.7. xAI inference is externally hosted, so only approved synthetic questions and evidence may be sent to it. The approved sequence is in the [tenant bring-up and first-participant rehearsal runbook](docs/tenant_setup_runbook.md).

## Evidence and isolation

Reports under artifacts/lab02/<participant-id>/<run-id>/ contain only the published validated answer, claims, synthetic sources, service outcomes and safe telemetry. No raw provider drafts, credentials, profile contents, database connection strings or full vectors are displayed. Rejected draft text is not silently presented as a validated answer.

Local files are not cryptographically signed cloud attestations. Private workstation ownership protects them; recorded traces support review and must be corroborated during rehearsal. Participant IDs and directories alone are not authentication. Runtime checks use authenticated database SESSION_USER/CURRENT_SCHEMA and reject excessive privileges. The facilitator verifies OCI identity ownership separately.

## Development verification versus workshop execution

```powershell
python -m pytest labs/lab02_contract_rag/tests
python -m ruff check labs/lab02_contract_rag
```

Unit and UI tests use developer-only doubles to validate controls without consuming OCI. They are not displayed in the workshop, cannot satisfy cloud acceptance and do not claim real model execution. The legacy demo module and 20-case fixture set are developer regressions only. There is no offline fallback in the participant dashboard/runner/evaluator. Integration checks are opt-in and remain pending until authorized access is available.

## Validation, costs and cleanup

- [ ] 15 private identities/schemas, Chicago models, wallet/network and budget approved.
- [ ] All own-table checks pass; peer read denial validated against known-existing tables.
- [ ] Nine-chunk corpus loaded in each schema and compatible calibration frozen.
- [ ] Dashboard shows actual answer, expected criteria and resolvable evidence.
- [ ] All 16 real scenarios and human rubric complete per participant.
- [ ] Real 15-person concurrent rehearsal records latency, failures, usage and throttling.
- [ ] No sample/fallback results or unexecuted scenarios counted as OCI success.

ADB, model calls and networking consume shared capacity/budget. See the capacity checklist for request counts without assumed prices or guaranteed throughput. On failure, record pending cloud validation and investigate; do not continue with simulated success. Stop/start and cleanup of the shared ADB require administrator coordination. Preserve reports under the approved retention policy; no automatic deletion or destructive migration is performed.
