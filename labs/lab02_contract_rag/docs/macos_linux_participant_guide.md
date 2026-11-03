# macOS and Linux participant guide

This guide is the supported participant route for macOS and Linux. It uses the same Python commands on both operating systems. The Windows PowerShell launchers remain an administrator/facilitator compatibility path and are not required here.

## Before the workshop

- Install Python 3.11 and Git.
- Receive your assigned OCI identity, database schema password through the approved handoff, wallet directory, and private participant session file.
- Store the wallet and session file outside the repository. The session file must be copied from `config/participant-session.env.example` and must never contain a password, token, private key, or secret.
- Confirm the wallet directory is readable only by the assigned participant where practical.

## Install locally

From the repository checkout:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
```

Use `python3` only if it already resolves to Python 3.11. Do not place the private session file inside the repository or commit it.

## Validate the private assignment

The command prompts locally for the database schema and wallet passwords. It does not invoke Generative AI or load data.

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-p001.env \
  --check-db
```

Expected output is safe JSON with `status` equal to `passed` and `database_session` equal to `participant_schema`.

## Prepare the approved synthetic corpus

Run only after the facilitator approves paid embeddings and synthetic loading. It prompts for local passwords, generates real OCI document embeddings, and writes only to the assigned schema.

```bash
python labs/lab02_contract_rag/scripts/ingest_oci.py \
  --session-file /private/path/lab02-p001.env \
  --confirm-live-inference \
  --confirm-synthetic-load
```

Expected output includes `STATUS ingested` and `OCI_EXECUTED True`.

## Freeze development calibration

Run after approved ingestion. The first command uses paid query embeddings; the second command is local and freezes the resulting calibration. Reuse existing private development measurements rather than collecting them again.

```bash
python labs/lab02_contract_rag/scripts/collect_calibration.py \
  --session-file /private/path/lab02-p001.env \
  --confirm-live-inference

python labs/lab02_contract_rag/scripts/calibrate.py \
  --measurements /private/path/development-measurements.json \
  --output /private/path/calibration.json
```

Distance overlap can occur in this small corpus. It does not make a candidate valid evidence; claim/evidence validation remains required.

## Use the local dashboard

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-p001.env
```

Open `http://127.0.0.1:8502` in the local browser. The dashboard remains local to the participant device. Each paid request requires a fresh acknowledgement and password entry. Do not expose the local port through a public proxy.

## Run one approved query from the command line

```bash
python labs/lab02_contract_rag/scripts/run_live_validation.py \
  --session-file /private/path/lab02-p001.env \
  --question "In v2, what method and endpoint update settlement status?" \
  --contract-version v2 \
  --confirm-live-inference
```

The command writes the private evidence report under `LAB02_REPORT_ROOT`. Do not treat a local test, a report from another participant, or a failed OCI call as workshop completion.

## Troubleshooting

- `HTTP_401` from query embeddings: reauthenticate the assigned OCI profile, validate it with an approved read-only OCI command, and obtain retry approval.
- `ORA-01017`: re-enter the assigned schema password; do not change the schema or table.
- Dashboard cannot start: confirm Python 3.11, the activated `.venv`, private session path, and port 8502 availability.
- Wallet error: validate the wallet directory and service alias privately; never paste wallet files or error bodies into chat or reports.

Run the macOS/Linux preflight on at least one actual macOS and one actual Linux device before the workshop. Unit tests on another operating system do not prove wallet, OCI profile, local browser, or network compatibility.
