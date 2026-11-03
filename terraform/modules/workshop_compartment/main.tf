resource "oci_identity_compartment" "workshop" {
  count = var.create_compartment ? 1 : 0

  compartment_id = var.parent_compartment_id
  name           = var.compartment_name
  description    = var.description
  enable_delete  = false
  freeform_tags  = var.freeform_tags
}
