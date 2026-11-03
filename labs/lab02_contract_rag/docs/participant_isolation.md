# Lab 2: one tenant, individual participant sessions

## Operating model

Use **one Chicago tenancy (`us-chicago-1`), one project compartment and one Autonomous AI Database** for Workshop 2. Every participant executes independently with an individual OCI IAM identity/profile, database user/schema, private local configuration, own vector table and evidence directory. The facilitator is the only platform administrator. No trial or ADB per participant is required. This supersedes Lab 2's previous per-team runner model; it does not change Lab 1's current deployment instructions.

| Boundary | p001 | p002 | Shared |
|---|---|---|---|
| Database user/schema | KHIPU_L2_P001 | KHIPU_L2_P002 | Same ADB service |
| Vector table | Own LAB02_CONTRACT_CHUNKS | Own LAB02_CONTRACT_CHUNKS | Same schema definition |
| OCI identity/profile | Individual | Individual | Approved inference-only IAM group |
| Execution | Private workstation/Cloud Shell session | Private workstation/Cloud Shell session | Same source checkout revision |
| Reports | artifacts/lab02/p001/run-id | artifacts/lab02/p002/run-id | Same report format |
| Documents/models | Independently loaded vectors | Independently loaded vectors | Same synthetic corpus/model selection |

The participant code is an organizational label, not authentication. Changing p001 to p002 does not grant access; a valid individual database credential is required. File directories are not an operating-system security boundary. Use separate OS accounts/workspaces or private Cloud Shell sessions; do not share a writable checkout containing private session files across people. Never share IAM API keys, token files or database passwords.

## Administrator preparation after approval

1. Create the shared infrastructure only through the separately approved Terraform process. Confirm Chicago model availability, quota, network, cost owner and required tags. The lab does not provision tenancy/ADB/IAM.
2. Assign opaque codes p001 through p999 in a private roster. Keep identity-to-code mappings and completed session files out of Git and public artifacts. The CSV example contains no secrets.
3. Review platform/bootstrap/06_create_lab02_participant.sql. With an approved administrator identity, run platform/bootstrap/create_lab02_participant.py for each new participant only after explicit approval. The script requires --confirm-create-participant and --participant-id. Administrator and new participant passwords are entered through getpass, not arguments or SQL substitution. Configure LAB02_BOOTSTRAP_USERNAME, ADB_CONNECT_STRING and ADB_WALLET_DIR privately.
4. Each new user gets CREATE SESSION, CREATE TABLE and a 128M DATA quota. No roles, ANY privileges, cross-schema grants or public synonyms are added. Existing usernames stop the script; credentials and permissions are not silently reused or reset. DDL can commit partially on failure: audit privately before retrying; never delete automatically.
5. Prepare the v2 table once per participant using `platform/bootstrap/create_lab02_participant_table.py`, connected as that participant with the approved dimension. The script requires `--confirm-create-table`, validates the authenticated schema and refuses an existing table. The same unqualified table name belongs to distinct owners. No migration from a team schema is performed automatically.
6. Audit direct and role-derived grants, including PUBLIC object grants; none may expose another participant's lab table. A schema owner can grant access to their own objects, so repeat the denial check if grants change. Administrator access remains intentionally outside participant isolation.
7. Deliver each participant's own credentials/profile, protected wallet access and completed session template through an approved private channel. An ADB wallet alone does not identify the participant; database authentication remains individual. The runner must never use administrator credentials.

Bootstrap is administrator preparation, outside the 180-minute session. No scripts in this update have been run against OCI.

## Participant session

Copy config/participant-session.ps1.example to the participant's ignored private directory and replace all placeholders with approved values. The roster must match, for example p001 and KHIPU_L2_P001. Dot-source the completed private file in that participant's own terminal. Environment settings take precedence over the optional local .env.

```powershell
# Use the assigned private participant session; this value alone does not authenticate.
$env:LAB02_PARTICIPANT_ID = "p001"
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
python labs/lab02_contract_rag/scripts/run_dashboard.py
```

For OCI, LAB02_PARTICIPANT_ID is mandatory and ADB_USERNAME must equal its assigned schema. Table identifiers must be unqualified, so a peer owner cannot be supplied as the table configuration. After authenticating, the runner verifies SESSION_USER and CURRENT_SCHEMA and rejects administrative roles and ANY privileges before touching corpus data. All OCI entry points use this checked connection factory.

The selected region is Chicago. SDK/CLI authentication, database connectivity, account assignment and network approval still require actual tenant validation. The code cannot prove that two differently named OCI profiles represent different people: the facilitator verifies the private IAM roster and independent identities before handoff.

## Isolation acceptance: two participants

The administrator first confirms that both participant users and their LAB02_CONTRACT_CHUNKS tables really exist. This is essential: an absent table can produce the same error as denied access.

From p001's private session:

```powershell
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
python labs/lab02_contract_rag/scripts/validate_isolation.py --peer-participant-id p002 --confirm-peer-table-ready
```

Repeat from p002 against p001. These probes are read-only and do not access row content. Accept only known access-denial errors for a known-existing peer table; successful reads or unrelated errors fail the gate. The own-table check must pass independently.

After paid inference and synthetic load approval, each participant runs their own ingestion, retrieval, generation and evaluation from the participant README. A facilitator may distribute the same frozen calibration if corpus/model/region/dimension match; this does not share mutable participant data. Each participant's nine vectors and table remain independent.

Required evidence per participant:
- Own account/schema match and own table readable.
- Cross-participant read denied in the two-person rehearsal, with administrator existence attestation.
- Own nine-chunk ingestion and scope-filtered retrieval.
- Own generated answer/citations and correct abstention.
- Own acceptance report and individual human rubric.

CLI output-dir is a root; ingestion/demo/evaluation add the participant namespace and a unique run directory. They never default to a shared team folder. Developer-only practice defaults to p001 only as a demonstration; set the assigned code for a multi-person event. Changing artifact IDs does not change the frozen contract hashes or document versions.

## Cost, rollback and cleanup

One shared ADB reduces duplicated infrastructure, but per-participant vector loads and inference consume shared capacity and budget. Budget and quota reviews must use participant count; stagger embedding/evaluation batches if needed. IAM inference-only access does not impose a per-person spending cap by itself. Coordinate shared ADB stop/start windows with everyone.

Old team schemas and reports are left intact. Configure new participant accounts and complete a two-person rehearsal before replacing the old exercise. Cleanup, password resets, grant changes and resource deletion require separate administrator approval. No automatic revocation or destruction is performed.

References: [Oracle session context](https://docs.oracle.com/en/database/oracle/oracle-database/26/sqlrf/SYS_CONTEXT.html), [Oracle user accounts](https://docs.oracle.com/en/database/oracle/oracle-database/26/dbseg/creating-user-accounts.html).

## Real-service dashboard update

The event has 15 participants (p001-p015). Participant dashboards run locally and invoke real OCI services only. Individual history excludes local demos and simulated fixtures. See dashboard_operations.md and capacity_15.md. The 16-case workshop reference replaces the mixed 20-case developer fixture set for cloud acceptance. No claims of actual OCI capacity are made until the real rehearsal passes.
