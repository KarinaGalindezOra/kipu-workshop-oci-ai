# Khipu OCI AI Workshop

This repository contains reproducible workshop assets for three OCI AI labs:

1. Decision memory, context isolation, and OCI-measured token comparison.
2. Versioned API-contract RAG with evidence.
3. API change analysis, patch generation, and regression tests.

## Operating model

- `trial-chicago` is the current technical rehearsal environment in `us-chicago-1`.
- `trial-team` is the reusable disposable profile for one workshop team. It never creates an OCI trial account; it operates after the facilitator creates that trial.
- `khipu` is a parameterized target environment that is not deployed until Khipu approves IAM, network, region, and budget decisions.
- A team trial has one ADB and one Agent Memory store. Each participant executes from their own workstation or Cloud Shell session with an individual temporary application database user.
- Only synthetic data belongs in the labs.

> Lab 2 operating-model override: one shared Chicago tenancy and ADB; one isolated user/schema, OCI identity, local session and evidence namespace per participant. See labs/lab02_contract_rag/docs/participant_isolation.md. The trial-per-team description remains the existing Lab 1 model.

## Repository layout

```text
docs/                 Architecture, readiness, security, and facilitation documents.
labs/                 Participant-facing laboratory material and code.
platform/bootstrap/   Idempotent post-provisioning SQL and Python setup.
terraform/            Parameterized OCI infrastructure.
```

## Local setup

Use Python 3.11.9.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab01,lab01-gateway,lab03,ui]"
python -m pytest
```

Copy `.env.example` to `.env` only for local configuration. Do not commit `.env`, wallet files, keys, passwords, or Terraform state.

## Terraform

Terraform must be reviewed before any apply. The default configuration is safe-by-default: it does not create IAM policies or an Autonomous Database unless explicit variables enable them.

```powershell
Set-Location terraform\environments\trial-team
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
```

Do not run `terraform apply` until the OCI Trial preflight, cost review, and explicit approval are complete. The default team profile does not create ADB, Object Storage, or IAM policies.

## Validation gates

- Python local tests pass without OCI access.
- Terraform formatting and validation pass after provider initialization.
- Trial Chicago preflight confirms OCI session, selected region, model discovery, and service limits.
- Each lab passes its evidence gate before the facilitation rehearsal.

See `docs/architecture.md` and `docs/tenant-readiness.md` before creating cloud resources.

Before provisioning the customer environment, follow the gated [Khipu preprovision runbook](docs/khipu-preprovision-runbook.md). It defines the team operating model, IAM boundary, database-schema bootstrap, network decision, rehearsal gates, and go/no-go checklist.

## Participant instructions

The Spanish participant guides use a progressive workshop format: goal, timebox, prerequisites, numbered steps, expected result, common errors, and an evidence gate for every lab.

- [Workshop guide and prework](docs/participant-guides/README.md)
- [Workshop 1: Token economy and decision memory](docs/participant-guides/01-decision-memory.md)
- [Lab 2: Versioned contract RAG with evidence](docs/participant-guides/02-contract-rag-evidence.md)
- [Lab 3: Safe API change](docs/participant-guides/03-safe-api-change.md)
