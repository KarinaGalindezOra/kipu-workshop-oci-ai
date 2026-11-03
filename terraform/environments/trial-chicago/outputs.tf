output "workshop_compartment_id" {
  value = module.workshop_foundation.workshop_compartment_id
}

output "workshop_bucket_name" {
  value = module.workshop_foundation.workshop_bucket_name
}

output "autonomous_database_id" {
  value = module.workshop_foundation.autonomous_database_id
}

output "reviewable_participant_policy_statements" {
  description = "Statements that Terraform would apply when iam_policies_enabled is true; this output alone does not prove that an IAM policy exists."
  value       = module.workshop_foundation.reviewable_participant_policy_statements
}

output "iam_policies_enabled" {
  description = "Whether this Terraform configuration is allowed to create the workshop IAM policy."
  value       = var.enable_iam_policies
}
