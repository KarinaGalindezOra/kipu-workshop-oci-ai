output "policy_id" {
  description = "Created IAM policy OCID, or null when policy creation is disabled."
  value       = try(oci_identity_policy.workshop[0].id, null)
}

output "participant_statements" {
  description = "Reviewable participant policy statements."
  value       = local.participant_statements
}

output "team_object_policy_statements" {
  description = "Optional reviewable team-scoped Object Storage policy statements."
  value       = local.team_object_statements
}

output "facilitator_statements" {
  description = "Reviewable facilitator policy statements."
  value       = local.facilitator_statements
}
