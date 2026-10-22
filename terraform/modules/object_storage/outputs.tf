output "bucket_name" {
  description = "Created bucket name, or null when disabled."
  value       = try(oci_objectstorage_bucket.workshop[0].name, null)
}

output "bucket_id" {
  description = "Created bucket OCID, or null when disabled."
  value       = try(oci_objectstorage_bucket.workshop[0].id, null)
}
