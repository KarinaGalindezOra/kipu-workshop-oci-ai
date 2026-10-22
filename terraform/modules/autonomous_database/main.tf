resource "oci_database_autonomous_database" "workshop" {
  count = var.enabled ? 1 : 0

  compartment_id              = var.compartment_id
  admin_password              = var.admin_password
  compute_model               = "ECPU"
  compute_count               = var.compute_count
  data_storage_size_in_tbs    = var.data_storage_size_in_tbs
  db_name                     = var.db_name
  display_name                = var.display_name
  db_version                  = var.db_version
  db_workload                 = "OLTP"
  is_auto_scaling_enabled     = var.is_auto_scaling_enabled
  is_mtls_connection_required = var.is_mtls_connection_required
  is_free_tier                = false
  license_model               = var.license_model
  freeform_tags               = var.freeform_tags
}
