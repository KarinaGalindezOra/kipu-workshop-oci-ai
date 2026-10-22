locals {
  participant_statements = [
    "allow group ${var.participant_group_name} to use generative-ai-chat in compartment ${var.workshop_compartment_name}",
    "allow group ${var.participant_group_name} to use generative-ai-text-embedding in compartment ${var.workshop_compartment_name}",
    "allow group ${var.participant_group_name} to inspect generative-ai-model in tenancy",
  ]

  team_object_statements = flatten([
    for access in values(var.team_object_access) : [
      "allow group ${access.group_name} to manage objects in compartment ${var.workshop_compartment_name} where all {target.bucket.name='${var.bucket_name}', target.object.name='${access.object_prefix}/*', any{request.permission='OBJECT_CREATE', request.permission='OBJECT_READ'}}",
    ]
  ])

  facilitator_statements = [
    "allow group ${var.facilitator_group_name} to manage autonomous-database-family in compartment ${var.workshop_compartment_name}",
    "allow group ${var.facilitator_group_name} to manage object-family in compartment ${var.workshop_compartment_name}",
    "allow group ${var.facilitator_group_name} to use generative-ai-family in compartment ${var.workshop_compartment_name}",
    "allow group ${var.facilitator_group_name} to inspect generative-ai-model in tenancy",
  ]
}

resource "oci_identity_policy" "workshop" {
  count = var.create_policies ? 1 : 0

  compartment_id = var.tenancy_ocid
  name           = var.policy_name
  description    = "Least-privilege workshop access for synthetic Khipu OCI AI labs."
  statements = concat(
    local.participant_statements,
    local.team_object_statements,
    local.facilitator_statements,
  )
  freeform_tags = var.freeform_tags
}
