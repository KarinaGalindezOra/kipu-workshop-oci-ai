output "workshop_compartment_id" {
  value = module.compartment.id
}

output "workshop_compartment_name" {
  value = module.compartment.name
}

output "workshop_bucket_name" {
  value = module.object_storage.bucket_name
}

output "autonomous_database_id" {
  value = module.autonomous_database.id
}

output "reviewable_participant_policy_statements" {
  value = module.iam.participant_statements
}

output "reviewable_team_object_policy_statements" {
  value = module.iam.team_object_policy_statements
}

output "reviewable_facilitator_policy_statements" {
  value = module.iam.facilitator_statements
}
