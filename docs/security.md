# Security Baseline

- Use only synthetic workshop data.
- Store no credentials, wallet files, API keys, or Terraform state in Git.
- Use one child compartment dedicated to the workshop.
- Use least-privilege IAM policies and review them before apply.
- Do not grant generic participant Object Storage access by default. When direct upload is approved, use a distinct team group and a team-scoped prefix with create/read permissions only.
- Use team-scoped Agent Memory identifiers and metadata filters.
- Use a different database schema and database user per team; keep the ADMIN account with the facilitator only.
- Prefer OCI Vault for Khipu deployment secrets.
- Treat Trial resources as disposable; remove them only after an explicit cleanup approval.
- The local Lab 1 gateway signer is a facilitator-only rehearsal secret. It belongs in the process environment or an approved secret store, never in a bundle, command history, participant terminal, or repository.

## Memory-specific controls

Agent Memory may persist messages, summaries, facts, and guidelines. The labs must:

- avoid personal, customer, or production data;
- use explicit `team_id` scopes;
- limit message and retrieval sizes;
- collect only aggregate workshop metrics; and
- provide a reset script for workshop-created memory records.
- derive the memory team scope from a verified server-side identity; do not trust a `team_id` supplied by a browser or JSON request.
