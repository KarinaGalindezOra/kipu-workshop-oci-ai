# Tenant Readiness Checklist

## Trial Chicago preflight

- [ ] OCI Trial tenancy created with `us-chicago-1` selected.
- [ ] OCI CLI session is valid.
- [ ] Current principal can inspect compartments, Object Storage, Autonomous Database, and Generative AI models.
- [ ] On-demand chat and embedding models are discovered in Chicago.
- [ ] Service limits and available credits are reviewed.
- [ ] A dedicated workshop child compartment name is approved.
- [ ] Data classification is confirmed as synthetic and non-sensitive.

## Khipu onboarding questions

- [ ] Confirm subscribed OCI regions and data-residency constraints.
- [ ] Identify the tenancy administrator who can approve IAM policies and resource creation.
- [ ] Confirm participant count and OCI IAM identities.
- [ ] Assign a workshop runner for each team and select the credential-handoff or facilitator-managed ADB model.
- [ ] Decide whether Cloud Shell and public Autonomous Database connectivity are permitted.
- [ ] Confirm credits, budget owner, expiration date, and maximum spend.
- [ ] Confirm whether a dedicated workshop compartment can be created.
- [ ] Authorize a pre-workshop deployment and end-to-end rehearsal.
- [ ] Confirm the ADB owner of `DBMS_AGENT_MEMORY_STORE`, supported delegation approach, and least-privilege workshop schema.
- [ ] Execute the Lab 1 synthetic seed and bidirectional exact-`user_id` isolation validation for `guideline` records in the Khipu tenancy.
- [ ] Approve the Lab 2 embedding model and its vector dimension in the selected Khipu region.
- [ ] Prepare a new Lab 2 schema/table per participant in the shared Chicago ADB; validate both own access and peer denial.
- [ ] Run the two synthetic contracts through ingestion and prove that a `v2`-filtered vector query returns only v2 evidence.
- [ ] Rehearse a chat-model answer that is limited to retrieved content, then attach version, source and section from retrieved metadata in the application layer. Confirm that an unsupported question is refused.
- [ ] Confirm each Lab 3 team can install the local FastAPI dependencies and run the synthetic v1-to-v2 regression tests.
- [ ] If the OCI chat-assisted analysis is used, approve the model and enforce the synthetic-source-only prompt rule.
- [ ] Confirm that Lab 3 participants have no production repository write, deployment, API-execution, or credential access during the exercise.
- [ ] Confirm whether Object Storage ingestion is facilitator-managed or requires one pre-existing IAM group and prefix per team.
- [ ] Review the team-scoped object policy statements and confirm that they contain only `OBJECT_CREATE` and `OBJECT_READ` for the approved team prefix.
- [ ] Run the non-destructive team-schema bootstrap once per team and record the schema owner outside the repository.

## Required validation commands

Run only after the OCI CLI has been configured:

```powershell
oci --version
oci session validate
oci iam region list --output table
oci iam compartment list --compartment-id $env:OCI_TENANCY_OCID --all --output table
oci generative-ai model-collection list-models --compartment-id $env:OCI_COMPARTMENT_ID --output table
```

Model discovery must select the actual chat and embedding model IDs used by the lab. Do not hardcode model IDs before this preflight.

## Lab 2 individual execution override

One shared tenant and ADB; each participant has an individual OCI identity/profile and database schema. Never use a shared team runner or database login for Lab 2. The administrator prepares accounts and tables, then each participant executes independently. See labs/lab02_contract_rag/docs/participant_isolation.md.
