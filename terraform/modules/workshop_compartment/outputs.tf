output "id" {
  description = "Workshop compartment OCID."
  value       = var.create_compartment ? oci_identity_compartment.workshop[0].id : var.existing_compartment_id
}

output "name" {
  description = "Workshop compartment name."
  value       = var.create_compartment ? oci_identity_compartment.workshop[0].name : var.existing_compartment_name
}
