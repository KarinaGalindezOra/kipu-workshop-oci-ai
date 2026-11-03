# Khipu Workshop Preprovision Runbook

## Purpose

Prepare the Khipu tenancy for the three OCI AI workshop labs without exposing customer data, shared credentials, or production resources. This runbook is a gated plan: no resource creation, IAM policy application, database user creation, or wallet distribution is authorized until Khipu approves the relevant gate.

> Lab 2 override: one shared Chicago tenancy/ADB with individual participant schemas. Follow [Lab 2 participant isolation](../labs/lab02_contract_rag/docs/participant_isolation.md); trial-per-team and shared-runner assumptions below do not apply to Lab 2.

## Recommended operating model

Use one disposable OCI trial per workshop team and teams of three to four participants. Each team trial has one dedicated compartment, one Autonomous AI Database, and one Agent Memory store. Every participant executes the SDK from their own workstation or Cloud Shell session with an individual temporary application database user; the platform facilitator is the only administrator.

| Component | Recommended model | Reason |
| --- | --- | --- |
| OCI identity | One participant group for approved Generative AI inference; one existing group per team only when direct Object Storage upload is approved | Keeps model inference simple and isolates Object Storage only where needed |
| Autonomous AI Database | One database per team trial; one owner and one temporary application user per participant | Isolates teams at the trial boundary while letting every participant execute directly |
| AI Agent Memory | One owner-managed store per team trial with participant users using `SchemaPolicy.REQUIRE_EXISTING` | Creation is serialized; direct SDK execution is real and controlled |
| Object Storage | Facilitator-managed by default; optional team prefix and group for direct synthetic file upload | Avoids sharing broad object-delete or overwrite permission |
| Lab 3 | Local synthetic FastAPI repository | Requires no OCI resource, database credential, or production repository access |

Do not grant participants OCI `manage autonomous-database-family`; database login rights are separate from OCI IAM and must be limited to their temporary application user.

## Decisions Khipu must approve

| Gate | Owner | Decision | Required before |
| --- | --- | --- | --- |
| G1 | Khipu tenancy administrator | Region, child compartment, IAM groups, and identity-domain naming | Terraform plan |
| G2 | Security and network owner | Cloud Shell use, ADB public or private connectivity, and wallet handoff method | ADB creation |
| G3 | Budget owner | ADB ECPU/storage, inference budget, and shutdown window | Terraform apply |
| G4 | Database owner | Team-schema pattern, quotas, and Agent Memory store owner | Database bootstrap |
| G5 | Workshop lead | Team count, runner identity, and rehearsal schedule | Credential handoff |

## Indicative preparation timeline

These are active-work estimates and exclude waiting for approvals.

| Timing | Activity | Estimate | Evidence |
| --- | --- | ---: | --- |
| T-10 business days | Complete G1-G3 and confirm participant identities | 60-90 minutes | Approved decision record |
| T-7 business days | Prepare the Khipu Terraform values and review the no-change plan | 45 minutes | Saved plan review |
| T-5 business days | Apply approved foundation and create team schemas | 60 minutes plus 15 minutes per team | Resource and schema checklist |
| T-3 business days | Rehearse all three labs with synthetic data | 120 minutes | Evidence artifacts and issue log |
| T-1 business day | Confirm runner access, model availability, ADB state, and contingency owner | 45 minutes | Go/no-go checklist |
| Workshop day | Start ADB, run a smoke test, and retain a facilitator rollback path | 20-30 minutes | Smoke-test results |

## IAM design

### Participant group

The shared participant group requires only OCI Generative AI inference and model discovery:

```text
allow group '<identity-domain>'/'<participant-group>' to use generative-ai-chat in compartment <workshop-compartment>
allow group '<identity-domain>'/'<participant-group>' to use generative-ai-text-embedding in compartment <workshop-compartment>
allow group '<identity-domain>'/'<participant-group>' to inspect generative-ai-model in tenancy
```

En un tenant cuyo grupo vive en el dominio predeterminado, usa `Default` como
`<identity-domain>`. Mantenerlo explícito hace trazable la relación entre la identidad de la
participante, el grupo y la política efectiva.

These permissions let participants invoke chat and embedding inference. They do not permit creation of dedicated AI clusters, management of Autonomous Database, or management of IAM policies.

If Khipu wants to restrict inference to the approved model IDs, add the OCI IAM `target.model.id` condition only after the final chat and embedding model IDs have been selected in the target region.

### Optional team Object Storage groups

The default Terraform configuration grants no Object Storage permission to the participant group. The facilitator uploads the fixed synthetic documents.

For direct team ingestion, create one existing IAM group per team and add only the members of that team. Set `team_object_access` only after group names and prefixes are approved. Terraform generates a statement equivalent to:

```text
allow group <identity-domain>/<team-group> to manage objects in compartment <workshop-compartment> where all {target.bucket.name='<workshop-bucket>', target.object.name='team-01/*', any{request.permission='OBJECT_CREATE', request.permission='OBJECT_READ'}}
```

This permits creation and reading of known paths under the team prefix. It intentionally omits listing, overwrite, and delete permissions. A common participant group with a common prefix is organizational only; it is not inter-team isolation.

### Facilitator group

The facilitator group remains separate and may manage the workshop ADB and Object Storage in the workshop compartment. It must not receive tenancy-wide administrator access merely to conduct this workshop.

## Database model

For Lab 2, use one shared ADB and a dedicated user/schema per participant: `KHIPU_L2_P001`, `KHIPU_L2_P002`, and so on. The approved administrator uses [the participant bootstrap](../platform/bootstrap/create_lab02_participant.py) with bound password values; no existing users are modified automatically. Each participant has a 128M quota, CREATE SESSION and CREATE TABLE, no cross-participant grants or administrative roles.

Create the Lab 2 vector table separately in each participant schema after approval. Every participant performs their own ingestion, retrieval, generation and evaluation. Validate denied access in both directions between two known-existing participant tables. The older team bootstrap is not the Lab 2 path.

Lab 1 uses scoped retrieval through an exact Agent Memory `user_id` plus `record_types=["guideline"]`. The owner must first prove the Agent Memory privilege model using an application user with `SchemaPolicy.REQUIRE_EXISTING`. The scope proves retrieval behavior but is not row-level authorization; production requires an authenticated service and complementary database, IAM, and network controls.

## Network and credential decision

| Option | Use when | Controls | Recommendation |
| --- | --- | --- | --- |
| Cloud Shell with mTLS wallet | Khipu permits Cloud Shell and a secure handoff to each team runner | Keep wallet and database password in an approved secret channel; never in Git, chat, or Object Storage | Recommended for the workshop |
| Private ADB endpoint | Khipu requires private access | Confirm a reachable VCN path from the runner environment before provisioning | Use only after a pre-workshop connectivity rehearsal |
| No direct participant ADB access | Credential distribution is not approved | Facilitator performs the live ADB commands while teams drive the analysis and evaluate outputs | Safe fallback; retains workshop learning objectives |

Do not share an ADMIN password. Do not paste wallet archives or passwords into a terminal recording, repository, ticket, email, or model prompt.

## Terraform procedure

1. Copy `terraform/environments/khipu/terraform.tfvars.example` to a local `terraform.tfvars` outside source control.
2. Set the approved region, tenancy reference, existing or new workshop compartment selection, Object Storage namespace, required tags, and disabled flags.
3. Run `terraform init`, `terraform fmt -recursive`, `terraform validate`, and `terraform plan -var-file=terraform.tfvars`.
4. Review the exact resources and policy statements. The default plan must not create ADB, IAM policy, or Object Storage resources until the relevant flags are explicitly enabled.
5. After G1-G3 approval, enable only the approved resources and repeat the plan review. Apply only after an authorized Khipu administrator approves that reviewed plan.

Never place a database password in `terraform.tfvars`. Supply it interactively or through an approved secret mechanism outside source control.

## Rehearsal gates

### Lab 1

- Store owner and privilege model proven in Khipu ADB.
- Synthetic procedural memory seeded for two test teams.
- Bidirectional exact-`user_id` isolation test passes for `guideline` records.
- Approved on-demand Cohere-compatible chat model returns complete `usage` telemetry for two equivalent synthetic prompts.
- A rehearsal using a non-administrator participant identity confirms that the memory-retrieval prompt uses fewer provider-reported input tokens without failing response-quality criteria.

### Lab 2

- Approved embedding and chat model IDs available in the selected region.
- Each Lab 2 participant schema owns its vector table and passes identity and peer-denial checks.
- v2-filtered cosine retrieval returns only v2 evidence.
- Application attaches version, source URI, and section from database metadata.
- Unsupported question returns an insufficient-evidence response.

### Lab 3

- Each team has Python 3.11.9 and `.[dev,lab01,lab03]` dependencies installed.
- Synthetic v1-to-v2 analysis produces `PAY-001`, `PAY-002`, and `PAY-003`.
- FastAPI regression tests pass for accepted v2 and rejected legacy requests.
- No participant has production repository write, deployment, or API-execution authority.

## Go no-go checklist

- [ ] G1 through G5 approved and recorded.
- [ ] Terraform plan reviewed; only intended resources and IAM statements appear.
- [ ] Required OCI Generative AI models are available and approved in the selected region.
- [ ] ADB connectivity and credential handoff tested with a team runner or the safe fallback is selected.
- [ ] Team schema bootstrap and Lab 2 vector-table creation tested without destructive SQL.
- [ ] Lab 1 store-owner limitation resolved or facilitator-managed fallback approved.
- [ ] All three lab evidence gates pass using synthetic data.
- [ ] ADB start and stop owner is assigned for every workshop date.
- [ ] Rollback owner, escalation path, and expected shutdown time are agreed.

## Rollback and cleanup

Do not run destruction during the event. Stop the workshop ADB during idle periods only when the assigned owner confirms that no team is using it. After the final session, preserve the minimal evidence required by Khipu, then review a Terraform destroy plan with the Khipu owner. Database users, buckets, policies, and the compartment must be deleted only through an explicitly approved cleanup plan.
