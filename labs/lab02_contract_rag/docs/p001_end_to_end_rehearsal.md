# P001 end-to-end rehearsal

This is the facilitator's reproducible rehearsal for one real Workshop 2 participant. It uses the same local dashboard, participant schema, OCI embedding service, ADB vector search and OCI chat path used in the workshop. It is not a load test and it does not establish readiness for 15 concurrent participants.

Use only the approved synthetic corpus, synthetic questions and the private p001 assignment. Keep the wallet, session file, passwords, token material and evidence reports outside the repository.

## Completion criteria

The rehearsal is complete only when the following outcomes have been reviewed in the dashboard and recorded in the private rehearsal log:

- T01 and T03 are `answered`, have the expected version-scoped route, and expose valid selected evidence.
- T05 is `needs_clarification` with origin `application_control`; it must not call OCI.
- T10 is `insufficient_evidence`; it must not invent an SLA or publish a chat answer.
- Every published contractual claim has a resolvable citation, excerpt, source version, section and line span.
- The service trace and local report belong to p001, show no simulated mode, and contain no credential material.

## 1. Private assignment and local preflight

Complete this step before any paid inference. It validates the database schema, wallet and assignment without calling Generative AI.

On Windows, load the private PowerShell session in a dedicated terminal and run:

```powershell
. '<private-p001-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

On macOS or Linux, use the private dotenv session file instead:

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-p001.env \
  --check-db
```

Expected result: safe JSON with `status` equal to `passed` and `database_session` equal to `participant_schema`.

If the result is not passed, stop. Do not change the assigned schema, create replacement credentials or retry a failed password blindly. Follow `troubleshooting.md`.

## 2. Start the local dashboard

The default listener is local-only on port 8502. Use a different unused local port only when 8502 is already occupied.

Windows with the loaded private session:

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

macOS or Linux with a private dotenv session file:

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-p001.env \
  --port 8502
```

Open `http://127.0.0.1:8502`. Do not use a public proxy, shared browser profile or another participant's session.

## 3. Confirm corpus readiness

If p001 has not yet loaded the approved nine-chunk corpus, select **Prepare my synthetic corpus** in the dashboard. Confirm both the paid-inference and synthetic-load acknowledgements, then enter the local database and wallet passwords when prompted.

Expected result: the dashboard records real document embeddings and ADB insertion in the private p001 schema. If the corpus is already present, do not force a reload or delete rows. Confirm that the calibration file is the approved compatible private calibration before asking questions.

## 4. Execute and inspect the four gate cases

Run the following questions individually from the predefined dashboard list. For each paid request, confirm the explicit OCI consumption acknowledgement. Record the visible status and review the evidence before continuing.

| Case | Expected result | OCI behaviour to verify |
|---|---|---|
| T01 — v1 endpoint | `answered`; `PATCH /v1/disbursements/{disbursement_id}` | Query embedding, version-filtered vector search and chat occur. The selected evidence is the v1 status-endpoint section. |
| T03 — v2 settlement endpoint | `answered`; `PUT /v2/disbursements/{disbursement_id}/status` | Query embedding, v2-only vector search and chat occur. The selected evidence is the v2 settlement-status section. |
| T05 — ambiguous update | `needs_clarification` | Application control asks for a version. There must be no OCI embedding, vector search or chat call. |
| T10 — availability SLA | `insufficient_evidence` | Retrieval may occur, but the system must not publish an invented SLA or a chat answer without selected evidence. |

For T01 and T03, inspect all of the following in **Expected versus observed**, **Service execution**, and **Claims and verifiable evidence**:

- The observed answer matches the frozen reference facts and expected state.
- `version_scope_pass` and `citation_checks_pass` are true.
- The accepted evidence is marked separately from retrieved candidates.
- The selected excerpt directly states the claimed route.
- Candidate `cosine_distance` is interpreted only as proximity: a lower distance is not proof that the candidate supports the claim.
- The trace identifies ADB, query embedding, vector search and chat as independent operations with their own timing.

For T05 and T10, confirm that the dashboard clearly distinguishes an application decision from an OCI model answer. A correct abstention or clarification is a successful outcome for that case, not a failed answer.

## 5. Record the result safely

Refresh **My execution history** and verify that every report belongs to p001. Store only the safe run summary, status, timing, usage counters and human review outcome in the facilitator's private rehearsal log. Do not copy passwords, wallets, OCI profile files, full vectors, raw provider errors or rejected model drafts.

## 6. Decision after rehearsal

Approve p001 only when all four gate cases meet their completion criteria and a human has reviewed the cited excerpts. If an operational error occurs, mark the affected case pending, preserve its safe report and investigate privately. Do not replace it with a fixture, reference answer or local fallback.

After p001 passes, the remaining operational prerequisites are participant identities, isolated schemas/tables, private handoff, at least one macOS/Linux preflight and the selected workshop execution wave plan.
