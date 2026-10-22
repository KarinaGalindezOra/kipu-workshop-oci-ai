locals {
  team_suffix = lower(var.team_code)
  common_tags = merge(var.freeform_tags, {
    Environment      = var.environment
    Project          = var.project_name
    WorkshopTopology = "trial-team"
    WorkshopTeam     = upper(var.team_code)
    ManagedBy        = "Terraform"
  })
}

module "workshop_foundation" {
  source = "../../modules/workshop_foundation"

  tenancy_ocid                     = var.tenancy_ocid
  create_workshop_compartment      = var.create_workshop_compartment
  parent_compartment_id            = var.parent_compartment_id
  existing_compartment_id          = var.existing_compartment_id
  existing_compartment_name        = var.existing_compartment_name
  workshop_compartment_name        = "cmp-${var.project_name}-${local.team_suffix}-${var.environment}"
  workshop_compartment_description = "Disposable OCI AI workshop environment for team ${upper(var.team_code)}."
  object_storage_namespace         = var.object_storage_namespace
  workshop_bucket_name             = "${var.project_name}-${local.team_suffix}-assets"
  enable_object_storage            = var.enable_object_storage
  enable_autonomous_database       = var.enable_autonomous_database
  autonomous_admin_password        = var.autonomous_admin_password
  autonomous_compute_count         = var.autonomous_compute_count
  autonomous_storage_tbs           = var.autonomous_storage_tbs
  autonomous_db_name               = "KWS${upper(var.team_code)}"
  autonomous_display_name          = "${var.project_name}-${local.team_suffix}-adb"
  autonomous_db_version            = var.autonomous_db_version
  autonomous_auto_scaling_enabled  = var.autonomous_auto_scaling_enabled
  autonomous_mtls_required         = var.autonomous_mtls_required
  autonomous_license_model         = var.autonomous_license_model
  enable_iam_policies              = var.enable_iam_policies
  participant_group_name           = var.participant_group_name
  facilitator_group_name           = var.facilitator_group_name
  iam_policy_name                  = "${var.project_name}-${local.team_suffix}-policy"
  team_object_access               = {}
  freeform_tags                    = local.common_tags
}
