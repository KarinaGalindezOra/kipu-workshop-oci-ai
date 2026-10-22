output "id" {
  description = "Autonomous Database OCID, or null when disabled."
  value       = try(oci_database_autonomous_database.workshop[0].id, null)
}

output "connection_strings" {
  description = "Autonomous Database connection strings, or null when disabled."
  value       = try(oci_database_autonomous_database.workshop[0].connection_strings, null)
  sensitive   = true
}
