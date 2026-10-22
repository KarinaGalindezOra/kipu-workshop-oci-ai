# Terraform Foundation

## Safety model

The Terraform modules are parameterized for two environments:

- `environments/trial-chicago`: pilot in `us-chicago-1`.
- `environments/khipu`: customer target that stays disabled until the Khipu tenancy decisions are approved.

Defaults intentionally do not create IAM policies or an Autonomous Database. Review every plan before apply. Terraform state, `terraform.tfvars`, passwords, wallets, and private keys must remain local and out of source control.

## Provisioning boundary

Terraform can create the OCI foundation. Bootstrap scripts create database-level team schemas, tables, vector indexes, and synthetic data afterward. This separates tenancy/IAM authorization from database administration.

## Suggested execution sequence

```powershell
Set-Location terraform\environments\trial-chicago
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file=terraform.tfvars
```

Run `terraform apply` only after explicit approval of the plan, selected model IDs, projected cost, and Trial resource availability.

## Khipu preprovisioning

The `environments/khipu` configuration is disabled by default. Its participant policy grants OCI Generative AI inference only. It does not grant generic Object Storage access.

If Khipu approves direct synthetic-document upload, configure `team_object_access` with one pre-existing IAM group and one prefix per team. The generated policy grants `OBJECT_CREATE` and `OBJECT_READ` only for that prefix; it omits object listing, overwrite, and deletion. Review the rendered policy statements before enabling `enable_iam_policies`.

See [Khipu preprovision runbook](../docs/khipu-preprovision-runbook.md) for the approval gates, credential model, database bootstrap, rehearsal, and cleanup procedure.
