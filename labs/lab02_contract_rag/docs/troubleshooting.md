# Troubleshooting and operational limits

| Symptom | Early signal | Action |
|---|---|---|
| Wrong interpreter | validate_environment fails | Activate project .venv with Python 3.11.9 |
| Manifest mismatch | Local load fails before retrieval | Restore approved source bytes; review a new corpus revision separately |
| Old guide refers to payments | POST /payments appears | Use canonical disbursement README and current matrix |
| CLI works, SDK fails | Authentication/provider error | Independently validate approved profile, token expiry, SDK signer and region |
| Query embedding returns HTTP 401 while ADB remains available | `oci_query_embedding` fails with `authentication_or_authorization` in the private trace | Reauthenticate the assigned OCI session profile with `oci session authenticate --profile-name <profile-name>`, complete browser sign-in, then validate it with `oci --profile <profile-name> session validate --output json` before one approved controlled retry. Never copy token files between participants. |
| Wrong region | Model endpoint unavailable | Confirm OCI_REGION and subscribed target region; Chicago is the selected target |
| Model request rejected | Wrong family or unsupported dimensions | Use the approved GenericChatRequest chat adapter and model-specific embedding configuration |
| ADB inaccessible | Connection/table check fails | Verify private network, wallet, schema and approved new v2 table |
| Legacy table | Missing corpus/provenance columns | Prepare a new table/schema after approval; never drop automatically |
| Existing embedding differs | Load refuses reuse | Keep old records; use an approved separate embedding table |
| Calibration overlap | A negative candidate is closer than a positive one | Preserve positive development recall, record the overlap privately, and require evidence selection; do not tune on acceptance |
| Weak vector candidates | Similarity without answer support | Preserve insufficiency; a nearest neighbor is not proof |
| Unsupported paraphrase | validate_claims error | Inspect private model interaction; return exact source sentences with valid IDs |
| Both versions in a single target query | Scope validation error | Stop publication and inspect filters; never repair by silently discarding metadata |
| Conflict | Two texts for one version/section | Show both sources; require human source correction |
| Quota or latency | Timeout, throttling, slow first request | Inspect the service trace. `adb_connect` or `adb_connection_acquire` isolates wallet/TLS/session cost from embedding, vector search and chat. Stop/review budget; operator-controlled retry; record OCI segment pending |
| Secret-bearing provider error | Generic error_stage in report | Investigate privately; do not paste exception bodies into participant reports |

No public exception stack/body is necessary to complete workshop evidence. Real OCI failures must be recorded as pending validation, not passed tests. The unit/mocked suite requires no cloud access. Opt-in read-only integration uses RUN_OCI_INTEGRATION_TESTS=true and may prompt for wallet/database passwords; paid inference still uses explicit CLI acknowledgement.

Resource cleanup: identify project-owned resources and dependencies, retain reports for the approved period, obtain owner approval, then use the approved infrastructure runbook. No shared compartment, IAM policy, database, wallet or key should be deleted by a lab script.

Participant isolation failures: check LAB02_PARTICIPANT_ID, its KHIPU_L2_Pnnn username, effective SESSION_USER/CURRENT_SCHEMA, ANY privileges and DBA roles. Cross-schema reads must be denied against a known-existing peer table. Return misassigned credentials privately to the administrator; never change the participant code to bypass identity checks.

## Dashboard-specific checks

Start with the assigned private participant session and scripts/run_dashboard.py. The server listens on 127.0.0.1; there is no central participant selector or simulator. Missing configuration/password/calibration blocks execution. If a model draft fails validation, the dashboard reports an error rather than substituting a reference/local response. The application-control label means no model invocation occurred; it is never proof of generated content.

Compare the observed text with the independent reference and expand every source. A golden-answer pass requires the matching predefined question without manual scope overrides. Custom requests require human review; no expected answer is invented. A local/example/peer report is rejected by history loading. Refresh history after a new run.

OCI on-demand throttling is dynamic; record rate-limit failures and request an approved retry with spacing. No automatic bulk retry, mock response or local fallback is available. The evaluator stops on operational error and marks remaining scenarios not run.
