# Current status: real OCI dashboard with individual participants

Updated: 2026-11-03. The current participant route supersedes historical local/offline completion and mixed fixture acceptance below.

Delivered: local participant-bound Streamlit dashboard, real OCI actions shared with the CLI, actual-versus-expected answer view, source/claim inspection, own report history, separate per-request inference/load acknowledgements, masked transient credentials, recorded service outcomes and no offline/simulated fallback. The live participant matrix has 16 non-fixture scenarios; the 20-case set remains a developer regression only.

The deployment target is one Chicago tenant/ADB with individual OCI identities and database schemas. Workshop 1 is unchanged.

Verification performed: full repository suite 109 passed, 2 skipped after the connection-pool and safe-reporting changes. Dashboard/adapter checks use isolated developer tests; no such result is presented as real OCI acceptance. The authorized p001 rehearsal below provides limited real OCI evidence.

Start with scripts/run_dashboard.py from each participant's private session. Read docs/dashboard_operations.md and the current README. Preserve human review of the obtained answer, not merely a PASS flag.

## Authorized real OCI rehearsal — p001, Chicago

The individual p001 rehearsal used only the approved synthetic contracts and actual OCI services. Reports and private operational traces remain in the participant's local private evidence directory; this record deliberately excludes credentials, wallet paths, token material, run identifiers and provider exception bodies.

| Exercise | Expected behaviour | Observed result |
|---|---|---|
| T01: v1 endpoint | Answer with the documented v1 `PATCH` route and a resolvable v1 citation | `answered`; expected reference, version scope, citation checks, support recall and accepted-evidence precision passed |
| T03: v2 settlement endpoint | Answer with the documented v2 `PUT` route and a resolvable v2 citation | `answered`; expected reference, version scope, citation checks, support recall and accepted-evidence precision passed |
| T05: ambiguous version | Ask for the target version without querying OCI | `needs_clarification`, produced by application control; no model call |
| T10: availability SLA | Abstain because the contracts document no SLA | `insufficient_evidence`; no chat call was required |

Two successful positive requests also exercised actual ADB, query embedding, exact vector search and OCI chat. On the second observation, reuse of the participant-local ADB pool reduced `adb_connection_acquire` from about 1.54 seconds to about 0.59 seconds (roughly 62%). OCI chat remained the largest and variable component; the two observed positive end-to-end times were approximately 8.65 and 8.03 seconds. These are rehearsal observations, not a production SLO.

An expired local OCI CLI security token was correctly surfaced as an authorization failure during rehearsal. Reauthentication restored the approved profile and later actual calls succeeded. This is now an explicit participant preflight check.

---

## Historical implementation record (superseded where stated above)

# Implementation and validation record

Date: 2026-10-26. Scope: source implementation and local/mocked verification only.

## Delivered

- P0: canonical disbursement documentation, 180-minute runbook and observable exercises.
- P0: nine-chunk frozen manifest, richer source metadata and report schema 2.0.
- P0: local ingestion, version resolver, scoped retrieval, evidence selection and extractive claims.
- P0: OCI embedding/load/query/chat adapters, provenance-safe reuse, explicit region, native vectors and independent inference/load gates.
- P0: development measurement collection and context-bound frozen calibration.
- P0: participant guide, facilitator answer key, rubric and troubleshooting.
- P1: version comparison, conflict/injection/invalid-citation/provider fixtures, per-stage timing and provider usage when available.
- Bootstrap source correction: removed invalid CREATE INDEX system grant; the script was not executed against ADB.

## Verification performed

- Python 3.11.9 in the existing project .venv.
- Full repository suite: 124 passed, 3 skipped. One pre-existing Starlette/httpx deprecation warning remains outside Lab 2.
- Lab 2 Ruff checks pass.
- Local environment validation: manifest passes; ingestion exports nine chunks.
- Local acceptance matrix: 20/20 cases, including four explicitly simulated adversarial/provider cases.
- Smoke commands: local ingestion, positive/ambiguous/unsupported questions, comparison and evaluator.
- No OCI network calls, inference charges, resource provisioning, database changes, IAM execution or GitHub operations performed.

Artifacts for reproducible local verification are under artifacts/lab02/implementation-validation/. These are generated evidence, not source-controlled credentials or proof of OCI success.

## Gates still requiring the real environment

- [ ] Khipu confirms runner identities, region/models and budget owner.
- [ ] Administrator approves network, dedicated schemas and new v2 table preparation.
- [ ] Approved operator performs real synthetic ingestion and development calibration.
- [ ] Each participant runs the OCI acceptance matrix and records actual latency/usage.
- [ ] Independent reviewer signs the relevance/completeness rubric.
- [ ] Facilitator completes a timed rehearsal and confirms retention/cleanup ownership.

These gates require access, organizational decisions and explicit authorization for paid/mutating OCI operations. They are not represented as completed by local tests.

## Deferred by design

Object Storage, SQL execution, multilingual retrieval, general semantic entailment, ANN indexes, reranking, web/API interfaces and production deployment. The advanced CSV and SQL are review-only learning fixtures. The bounded recognizer is deliberately limited to English contract topics. Exact extraction validates provenance, not universal relevance or arbitrary contradictions.

## Rollback

The new database schema is incompatible with the historical table: create a separate approved table/schema, never mutate the old one automatically. Keep an approved manifest plus embedding configuration as a unit. To return to a previous run, select its approved corpus/table configuration. Resource destruction remains a separate owner-approved operation.

## Individual participant update

Workshop 2 now uses one Chicago tenant and one shared ADB with an individual OCI identity/profile, private session, database user/schema, vector table and evidence namespace per participant. `p001` maps to `KHIPU_L2_P001`; `p002` maps to `KHIPU_L2_P002`. The per-team runner model is superseded for Lab 2 only.

Delivered: administrator-only bound-parameter account bootstrap, private session/roster templates, mandatory OCI participant mapping, server-side session/schema/privilege checks, private output namespaces and read-only known-peer access-denial probes. Updated participant/facilitator guides, architecture, proposal and shared-readiness pointers.

Validation: 124 repository tests passed, 3 skipped; Ruff passed. Local p001 and p002 runs used separate directories, with a 20/20 local acceptance run. Session mismatch, excess privileges, peer-read success and unrelated connectivity errors are rejected by mocked checks. No tenant, database account, grant or resource has been created or modified in OCI. The actual bidirectional peer-denial rehearsal and independent OCI IAM identity check remain required.
