# Platform Bootstrap

Terraform creates OCI resources only. Bootstrap scripts create team-scoped schemas, vector tables, synthetic data, and reset routines after a secure Autonomous Database connection exists.

The scripts must be idempotent and must never contain an administrative password, wallet archive, or populated connection string.

## Team schemas

Run [01_create_team_schema.sql](01_create_team_schema.sql) as the approved database administrator once for every workshop team:

```text
@platform/bootstrap/01_create_team_schema.sql T01
```

The script prompts for the team password interactively, creates `KHIPU_WS_T01` only when it does not already exist, grants the minimum Lab 2 DDL privileges, and limits the user to a 512 MB quota. It does not reset an existing password and it does not delete data.

Use a password without single quotes, double quotes, or ampersands when running this SQLcl script. Deliver the resulting team credential only through the Khipu-approved secret-handoff process. Do not put passwords in shell history, command arguments, repository files, wallets, prompts, or chat.

The Lab 2 table script must be run while connected as the relevant team schema. The Lab 1 Agent Memory store remains facilitator-managed until its intended store-owner and privilege model have been validated in the Khipu tenancy.

## Workshop 2 individual schemas

Workshop 2 uses one schema per participant. After explicit approval, create only the assigned participant with `create_lab02_participant.py`, then create the vector table while authenticated as that participant:

```powershell
python platform/bootstrap/create_lab02_participant.py --participant-id p001 --confirm-create-participant
python platform/bootstrap/create_lab02_participant_table.py --participant-id p001 --vector-dimension 1536 --confirm-create-table
```

Both commands prompt locally for passwords. Never enter a password as a command-line argument or add it to a session file. The table bootstrap validates the participant schema, refuses existing tables, creates only `LAB02_CONTRACT_CHUNKS` and its scope index, and grants no additional privileges.

For an interactive local launch without embedding private paths or passwords in source files, use `run_lab02_bootstrap.ps1` with explicit parameters for the wallet directory, TNS alias, participant code and operation mode.

If a schema bootstrap stops, do not retry it blindly. Use the launcher's `audit` mode first; it reports only the participant existence, account state, table presence, assigned system privileges, or a safe database error code.

After a private participant session file is prepared, run `run_lab02_participant_readiness.ps1` with that file path. It prompts for the participant database and wallet passwords, validates the authenticated schema and performs no inference or data mutation.

### Portable participant session files

The approved facilitator can generate a password-free cross-platform dotenv session for an assigned participant. It is an administrative preparation step, never a participant bootstrap command. The target participant profile does not need to exist on the facilitator workstation: `--bootstrap-profile` is used only to retrieve the approved workshop compartment metadata.

```powershell
python platform/bootstrap/create_lab02_private_session.py `
  --participant-id p002 `
  --profile-name KWS2_P002 `
  --bootstrap-profile KHIPU_WS2_ADMIN `
  --format dotenv `
  --portable `
  --output '<private-directory>/p002.env'
```

The generated file uses the portable `${HOME}/.khipu/lab02` directory convention and contains the assigned schema, region, approved models, ADB alias and workshop compartment only. It contains no password, token, private key or wallet password. The participant places the wallet in that private directory, authenticates their own OCI CLI profile, and receives the session file through the approved private channel.

For macOS and Linux participants, use the cross-platform [participant guide](../../labs/lab02_contract_rag/docs/macos_linux_participant_guide.md). It invokes the same Python runners with a private `.env` session file through `--session-file`; it does not replace the existing PowerShell administrator launchers.

After explicit approval of paid embeddings and synthetic loading, run `run_lab02_participant_ingestion.ps1` with that private session file. It invokes the approved embedding model, writes only to the participant schema and stores evidence reports in the private report root.

After successful ingestion and explicit approval, run `run_lab02_participant_calibration.ps1`. It creates private development measurements, reuses them rather than charging for another collection attempt, and freezes a candidate threshold that preserves positive recall. If negatives overlap by distance, the calibration records that fact and requires evidence selection; proximity alone never establishes support.

After calibration and per-query approval, run `run_lab02_participant_query.ps1`. It prompts locally for the participant database and wallet passwords, uses the provided version as a strict scope, and writes the real answer and evidence report beneath the private report root.

## Agent Memory owner password recovery

Use [06_reset_agent_memory_owner_password.sql](06_reset_agent_memory_owner_password.sql) only after an approved ADB administrator has confirmed that the team owner exists and is `OPEN`, and the owner credential is known to be unavailable or incorrect. It prompts for a replacement password locally and changes only that existing owner account:

```text
@platform/bootstrap/06_reset_agent_memory_owner_password.sql T01
```

Use a password without single quotes, double quotes, or ampersands. Store it only in the approved secret-handoff channel; do not place it in commands, files, chat, or the workshop dashboard.
