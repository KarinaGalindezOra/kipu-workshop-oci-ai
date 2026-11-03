# Team Trial Terraform Profile

This profile creates a disposable OCI foundation for exactly one workshop team.
It is the default Lab 1 topology and the technical contingency for a later Khipu
tenant deployment. It starts with all billable and IAM-sensitive capabilities disabled.

## Preconditions

- A disposable OCI trial already exists for the assigned team.
- The trial home region is known and is present in `terraform.tfvars`.
- The operator is authorized to create a child compartment and, later, an Autonomous Database.
- Required owner and cost tags have approved values.

## Safe preflight

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform fmt -recursive
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
```

The initial plan should create only the dedicated compartment. It must not create an
Autonomous Database, Object Storage bucket, or IAM policy.

After reviewing that plan, the operator can create only the compartment:

```powershell
terraform apply -var-file=terraform.tfvars
terraform output workshop_compartment_name
terraform output workshop_compartment_id
```

## Approved database deployment

After the cost review and explicit approval, enable the database in the private
`terraform.tfvars` file and provide the administrator password only through the
session environment:

```powershell
$secret = Read-Host -AsSecureString
$env:TF_VAR_autonomous_admin_password = [System.Net.NetworkCredential]::new('', $secret).Password
terraform plan -var-file=terraform.tfvars
# Review the plan output. Run apply only after confirming it is the intended ADB.
terraform apply -var-file=terraform.tfvars
$env:TF_VAR_autonomous_admin_password = $null
Remove-Variable secret
terraform output autonomous_database_id
```

Do not run `terraform apply` until the reviewed plan shows the intended team-only
resources. Terraform does not create OCI trial accounts; it operates after the trial
has been created by the facilitator team.

For the complete Console-to-participant walkthrough, use the [Lab 1 facilitator prework](../../../docs/facilitator-guides/01-decision-memory-prework.md).
