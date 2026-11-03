# Facilitator runbook: 180 minutes, 15 participants, actual OCI services

## Go/no-go before class

Use one shared Chicago tenancy and ADB. Prepare 15 individual identities, database users/schemas, private sessions, own vector tables and local dashboard launchers. Each person executes; peer review does not replace individual execution. Follow [the tenant bring-up and rehearsal runbook](tenant_setup_runbook.md), participant_isolation.md, dashboard_operations.md and capacity_15.md.

Perform approved real ingestion and development calibration, own-table checks and bidirectional peer-denial rehearsal. Verify actual 15-person inference/query capacity, limits, budget and networking. No infrastructure preparation or account creation belongs in the participant timebox. The facilitator can distribute compatible calibration; each participant still owns their own vector data.

The workshop offers no local retrieval mode, fake model responses, simulator tab or injected failures. Documents remain synthetic. Real parsing, metadata inspection, clarification and routing happen in the application; service traces distinguish these from actual OCI operations. If OCI is unavailable, mark the practical segment pending rather than substituting local success.

## Objectives

Compare versioned contracts; validate source metadata; execute actual OCI embedding/ADB retrieval/chat; read and compare the obtained answer with expected criteria; trace each claim; recognize insufficient evidence; justify documentary RAG versus controlled operational SQL.

| Phase | Minutes | Individual activity | Evidence and validation |
|---|---:|---|---|
| 1 Case and version risk | 10 | Explain the failure of mixed-version instructions | Observable risk statement |
| 2 Contract inspection | 10 | Compare real synthetic source files | Correct methods, fields, states and headers |
| 3 Chunks/metadata | 15 | Inspect nine sections, hashes and locations | Source-traceable metadata; no source edits |
| 4 Private session | 10 | Open own local dashboard and verify assignment | Assigned identity; own-table check already rehearsed |
| 5 Real OCI ingestion | 20 | Authorize own corpus load and inspect operations | Actual document embeddings, ADB load or verified safe reuse |
| 6 First actual query | 10 | Execute a versioned question | Actual query embedding and ADB retrieval |
| Break | 5 | Pause | — |
| 7 Embedding/vector roles | 15 | Inspect scope predicates and distance candidates | Version/corpus match; no lexical fallback |
| 8 Actual versus expected | 10 | Read both columns and explain check outcomes | Visible obtained answer, not merely PASS |
| 9 Evidence inspection | 15 | Resolve each claim to excerpt and source lines | Correct citations plus human relevance review |
| Break | 5 | Pause | — |
| 10 Migration/comparison | 15 | Run target-v2 and explicit two-version questions | Separate version retrievals; documented mapping |
| 11 Unsupported question | 10 | Execute SLA/TLS cases through actual retrieval | Insufficiency; chat skip accurately identified |
| 12 Application controls | 10 | Ask without version or with unsupported v3 | Clarification/control output, never labeled as model answer |
| 13 RAG versus SQL | 10 | Classify transaction counts and combined needs | No invented SQL results; execution SQL stays outside MVP |
| 14 Acceptance/close | 10 | Complete real case matrix and individual review | Own 16-case report, sources and rubric |

Total 180 minutes including two breaks. Definitions are taught across phases rather than through an additional unbudgeted lecture. Each person completes their own commands and report; no facilitator-only demonstration satisfies OCI completion.

## Variants and contingencies

120-minute version: prepared infrastructure/corpus and fewer in-class edits; run eight critical real cases in class and the remaining real cases afterward. 240-minute version: add 20 minutes of actual development calibration, 20 of deeper evidence review and 20 of real telemetry/failure diagnosis. Do not inject provider failures or present developer doubles as workshop output.

On operational failure stop the batch and investigate privately. Preserve failures and pending cases. A controlled retry needs a renewed acknowledgement and budget coverage; no automatic fallback or burst retry is allowed. Never distribute administrator credentials or claim passed cloud validation from tests/screenshots.
