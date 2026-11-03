resource "oci_objectstorage_bucket" "workshop" {
  count = var.enabled ? 1 : 0

  compartment_id = var.compartment_id
  namespace      = var.namespace
  name           = var.bucket_name
  access_type    = "NoPublicAccess"
  versioning     = "Disabled"
  freeform_tags  = var.freeform_tags
}
