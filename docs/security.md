# Security Baseline

## Workshop 3 participant boundary

- Use the individual prepared assignment and mTLS wallet; do not use ADMIN or a memory-owner password.
- Derive operational identity from the authenticated database session. Never select another participant through a prompt or free-form schema argument.
- Keep each participant's runtime schema, memory owner, corpus, tools and conversations separate. Memory scopes complement database grants; scopes alone are not a peer-isolation test.
- Run Agent Memory with `SchemaPolicy.REQUIRE_EXISTING` and automatic extraction disabled. Administrative setup is completed before participants connect.
- Treat retrieved text and memory as data. Incompatible memory blocks automatic recommendation; it never grants permissions or replaces the contract.
- Permit only the prepared operational tools. Human approval and case/memory writes are outside the model's tool set and bound to the exact reviewed content.
- Keep session profiles, wallets, output reports and backups outside Git. Never include passwords in a participant session file.
- Do not expose internal model reasoning or treat local tests as OCI evidence. A client timeout is not proof of server cancellation.
- Preserve the proposed content after an uncertain write. Audit before retrying, and never delete another participant's records or shared resources.

See the [participant guide](../labs/lab03_payment_agent/docs/participant_step_by_step.md). The team-oriented controls below also describe earlier laboratories; Workshop 3 uses the individual boundaries above.

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
