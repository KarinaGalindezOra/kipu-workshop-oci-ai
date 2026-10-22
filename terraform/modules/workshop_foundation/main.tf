module "compartment" {
  source = "../workshop_compartment"

  create_compartment        = var.create_workshop_compartment
  parent_compartment_id     = var.parent_compartment_id
  existing_compartment_id   = var.existing_compartment_id
  existing_compartment_name = var.existing_compartment_name
  compartment_name          = var.workshop_compartment_name
  description               = var.workshop_compartment_description
  freeform_tags             = var.freeform_tags
}

module "object_storage" {
  source = "../object_storage"

  enabled        = var.enable_object_storage
  compartment_id = module.compartment.id
  namespace      = var.object_storage_namespace
  bucket_name    = var.workshop_bucket_name
  freeform_tags  = var.freeform_tags
}

module "autonomous_database" {
  source = "../autonomous_database"

  enabled                     = var.enable_autonomous_database
  compartment_id              = module.compartment.id
  admin_password              = var.autonomous_admin_password
  compute_count               = var.autonomous_compute_count
  data_storage_size_in_tbs    = var.autonomous_storage_tbs
  db_name                     = var.autonomous_db_name
  display_name                = var.autonomous_display_name
  db_version                  = var.autonomous_db_version
  is_auto_scaling_enabled     = var.autonomous_auto_scaling_enabled
  is_mtls_connection_required = var.autonomous_mtls_required
  license_model               = var.autonomous_license_model
  freeform_tags               = var.freeform_tags
}

module "iam" {
  source = "../workshop_iam"

  create_policies           = var.enable_iam_policies
  tenancy_ocid              = var.tenancy_ocid
  workshop_compartment_name = module.compartment.name
  participant_group_name    = var.participant_group_name
  facilitator_group_name    = var.facilitator_group_name
  bucket_name               = var.workshop_bucket_name
  policy_name               = var.iam_policy_name
  team_object_access        = var.team_object_access
  freeform_tags             = var.freeform_tags
}
