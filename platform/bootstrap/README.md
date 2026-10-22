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

## Agent Memory owner password recovery

Use [06_reset_agent_memory_owner_password.sql](06_reset_agent_memory_owner_password.sql) only after an approved ADB administrator has confirmed that the team owner exists and is `OPEN`, and the owner credential is known to be unavailable or incorrect. It prompts for a replacement password locally and changes only that existing owner account:

```text
@platform/bootstrap/06_reset_agent_memory_owner_password.sql T01
```

Use a password without single quotes, double quotes, or ampersands. Store it only in the approved secret-handoff channel; do not place it in commands, files, chat, or the workshop dashboard.
