# Workshop 2 tenant bring-up and first-participant rehearsal

This runbook is for the facilitator and approved OCI administrator. It prepares one Chicago tenancy and one shared Autonomous AI Database for individual participant execution. It is not a participant handout and it must not be stored with credentials, wallets, connection strings, or OCI profile contents.

## Completion model

Each participant has an individual OCI identity, an individual database schema, an individual `LAB02_CONTRACT_CHUNKS` table, a private PowerShell session file, a private artifact root, and a local dashboard. The ADB service is shared. A successful local test, a mocked test, or another participant's report never establishes OCI completion for an individual.

The approved real services are the Chicago embedding model, Autonomous AI Database vector search, and the approved OCI chat model. All workshop documents, questions, and evidence are synthetic. Do not replace a real OCI failure with a local or simulated result.

## Prerequisites and approvals

Before provisioning, record the approved tenant, project compartment, region, cost owner, retention owner, participant roster, network route, wallet distribution mechanism, model IDs, and maximum workshop spend outside the repository. Confirm the following separately:

- Creating or resizing ADB and creating a child compartment.
- IAM group membership and least-privilege Generative AI policy changes.
- Each paid embedding or generation rehearsal.
- Distribution of individual credentials and private wallet access.
- Any retry after a quota, authentication, or operational failure.

Use a dedicated project child compartment. Apply the required project tags through the approved OCI process. Participants receive no administrator credential and no shared database schema password.

## Shared OCI preparation

1. Create the approved child compartment in Chicago and attach the required project tags.
2. Create one Autonomous AI Database with private or approved secured connectivity, mutual TLS, a dedicated database administrator, and capacity sized for the rehearsal. Keep the wallet outside the repository.
3. Create the participant IAM group and apply only the approved `generative-ai-family` policy in the project compartment. Add each participant's individual identity to that group.
4. Validate the OCI CLI profile, region, service-model availability, ADB status, network path, and wallet before creating any participant schema.
5. Run the real model preflight once with explicitly approved synthetic input:

```powershell
python labs/lab02_contract_rag/scripts/validate_environment.py --confirm-synthetic-external-inference
```

The preflight must show the approved embedding dimension and the selected chat model. For externally hosted models, retain only synthetic input and the safe result summary.

## Per-participant procedure

Repeat this procedure once for each assigned participant identifier. Run all commands from the repository root using the project virtual environment. Passwords are typed only into local prompts, never in arguments, files, command history, or reports.

1. Create the assigned database schema after explicit approval:

```powershell
python platform/bootstrap/create_lab02_participant.py --participant-id p001 --confirm-create-participant
```

Expected result: `LAB02_PARTICIPANT_SCHEMA_CREATED`.

2. Create the vector table while authenticating as that new participant:

```powershell
python platform/bootstrap/create_lab02_participant_table.py --participant-id p001 --vector-dimension 1536 --confirm-create-table
```

Expected result: `LAB02_PARTICIPANT_TABLE_CREATED`. The command refuses an existing table; it never replaces a legacy table.

3. Create the private participant environment/session file using the approved secret-handoff process. Store the file and wallet directory outside the repository. It must contain only that participant's identity, database mapping, private artifact root, calibration file path, region, and approved model configuration. Do not share it with another participant.

4. Validate the participant connection before inferencing:

```powershell
platform/bootstrap/run_lab02_participant_readiness.ps1 -SessionPath '<private-session-file>'
```

Expected result: a safe JSON result with `status` equal to `passed` and `database_session` equal to `participant_schema`.

5. After approving the synthetic load and paid embeddings, perform the real ingestion:

```powershell
platform/bootstrap/run_lab02_participant_ingestion.ps1 -SessionPath '<private-session-file>'
```

Expected result: `STATUS ingested`, `OCI_EXECUTED True`, and a private evidence report. Verify that the report records nine inserted synthetic chunks and real successful ADB and document-embedding operations.

6. After approving development embeddings, freeze a private calibration:

```powershell
platform/bootstrap/run_lab02_participant_calibration.ps1 -SessionPath '<private-session-file>'
```

The command reuses existing private development measurements when present; it must not charge for an unnecessary re-collection. A negative candidate can be closer than a positive one in this small corpus. That condition is recorded as `negative_overlap_detected`; it does not make distance evidence. The frozen candidate threshold preserves positive recall, while claim/evidence validation determines whether a candidate supports an answer.

7. With a separate per-query approval, run the first version-scoped real question:

```powershell
platform/bootstrap/run_lab02_participant_query.ps1 `
  -SessionPath '<private-session-file>' `
  -ContractVersion v2 `
  -Question 'In v2, what method and endpoint update settlement status?'
```

Expected result: a private evidence report containing the actual OCI answer, retrieved evidence, candidate distances, service operations, and expected-answer comparison. Review the answer and evidence manually before calling it correct.

8. Launch the local dashboard only after readiness, ingestion, and calibration are complete:

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py
```

It binds to `127.0.0.1` and must expose only that participant's private reports/configuration.

## Rehearsal gates

Run this sequence for the facilitator account and at least one non-facilitator participant before duplicating it. Then complete two real end-to-end rehearsals before the workshop: one positive v2 result and one negative/clarification result. Before the event, validate access isolation in both directions with two known existing participant tables, and conduct the approved 15-person Chicago concurrency rehearsal.

Do not count a service error, skipped call, local test, or manually edited report as a passed rehearsal. Store safe operation summaries and timestamps in the private rehearsal log; preserve no passwords, wallets, profile content, raw vectors, or raw rejected model drafts.

## Troubleshooting decision points

| Symptom | Safe next action |
|---|---|
| OCI session token has expired | Reauthenticate the assigned CLI profile in the browser, then repeat only the blocked read-only/preflight step. |
| Query embedding returns HTTP 401 while ADB access succeeds | Treat OCI inference authentication as expired or invalid. Reauthenticate the assigned session profile, validate it using a read-only OCI command, then obtain a new controlled-retry approval. |
| `ORA-01017` | Stop and re-enter the assigned participant credential; do not change the schema or table. |
| Password-policy error during schema creation | Use a new 16–64-character approved password with no whitespace or quote characters. Audit before retrying if the command reached ADB. |
| Schema bootstrap uncertainty | Run `run_lab02_bootstrap.ps1 -Mode audit` and inspect only its safe output before deciding whether to retry. |
| Provider 429 or timeout | Stop the batch, retain the pending status, check quota/budget, and obtain explicit approval for a spaced retry. |
| Development distances overlap | Keep the frozen candidate threshold only if positives are retained; require evidence selection and never present distance as proof. |
| Chat response fails claim validation | Publish no answer. Inspect private logs and report the operational error; do not substitute a reference answer. |

## Post-workshop cleanup

Retain reports according to the approved retention period. Identify project-owned resources and dependencies before proposing any cleanup. Database users, tables, wallet material, ADB, IAM policies, and the project compartment may be changed or deleted only by their owner after a separate explicit approval.
