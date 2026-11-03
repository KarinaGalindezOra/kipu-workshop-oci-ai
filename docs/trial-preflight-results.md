# Chicago Trial Preflight Record

Date: 2026-10-08

> Historical pilot only: the two-chunk payment example predates the current nine-section disbursement corpus. It does not certify the current Lab 2 runner or Khipu environment.

## Scope

Technical pilot validation of the OCI Free Trial tenancy in `us-chicago-1` using only synthetic workshop data.

## Confirmed

- Cloud Shell session is authenticated in the target region.
- Object Storage API is available.
- Autonomous Database API is available.
- Generative AI Playground exposes an on-demand chat model and an English embedding model.
- The active identity can list accessible compartments.
- A dedicated workshop compartment and Object Storage bucket were provisioned with Terraform.
- A 2-ECPU Autonomous AI Database was provisioned and reached `AVAILABLE`.
- The ADB wallet was generated only in the private Cloud Shell directory and was not copied to the repository.
- Oracle AI Agent Memory 26.8.0 was installed in a Python 3.12 Cloud Shell environment.
- A keyword-based Agent Memory store was initialized and tested with synthetic procedural guidelines for two teams.
- User-scoped retrieval with an exact `user_id` and `record_types=["guideline"]` returned each team's own guideline and did not return the other team's guideline.
- OCI Generative AI produced document and query embeddings for the two synthetic Lab 2 contracts with a matching vector dimension.
- A dedicated ADB vector table stored the two contract chunks and their version, section, source and content-hash metadata.
- A cosine-distance retrieval filtered to `contract_version = 'v2'` returned exactly the expected synthetic v2 payment-contract evidence.
- A current on-demand chat model answered a question using only the retrieved v2 fragment. The final answer envelope attached the version, source URI and section directly from the retrieved ADB metadata.

## Observations

- The Cloud Shell OCI CLI version does not implement base-model discovery through
  `oci generative-ai model list`; the console Playground was used for model validation.
- Cloud Shell includes Terraform `1.5.7`, while this repository requires Terraform `>= 1.6.0`.
- The foundation default for Autonomous Database is two ECPUs, with autoscaling disabled.
- The dedicated `LAB01_OWNER` schema could not create the Agent Memory store because the managed package returned insufficient privileges. The Free Trial ADB also rejected delegation of that package from `ADMIN`.
- The store was created under `ADMIN` only as a personal-trial validation exception. This is not the target Khipu tenant design.
- The previously selected on-demand chat model was retired. The current model accepted the grounded prompt but did not support the requested native citation mode. The workshop design therefore attaches citations in the application layer from retrieved metadata, which is the more reliable control.

## Not Performed

- No IAM policies, API keys, or customer data were created or submitted.
- No Terraform plan or apply will be run against the Khipu tenant until its own approval gates are complete.

## Next Change Gate

Before Khipu provisioning, confirm the ADB Agent Memory package-owner and delegation model,
then prove that a dedicated workshop schema can initialize and query a store with least
privilege. For Lab 2, approve the embedding and chat models, validate the matching vector
dimension, and rehearse the grounded-answer stage with source citations attached from
retrieved metadata. Review the
parameterized Terraform plan, approved IAM policies, network model, budget, and participant
operating model. Database and wallet passwords must be entered directly in Cloud Shell
without echo and must not be saved in source control, terminal history, or Terraform variable
files.
