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
  value = module.workshop_foundation.reviewable_participant_policy_statements
}

output "reviewable_team_object_policy_statements" {
  value = module.workshop_foundation.reviewable_team_object_policy_statements
}
