variable "enabled" {
  description = "Create Autonomous Database only after a reviewed plan and explicit approval."
  type        = bool
  default     = false
}

variable "compartment_id" {
  description = "Target compartment OCID."
  type        = string
}

variable "admin_password" {
  description = "ADB administrative password supplied at runtime; never commit it."
  type        = string
  sensitive   = true
  default     = null
  nullable    = true

  validation {
    condition     = var.admin_password == null ? true : length(var.admin_password) >= 12
    error_message = "The Autonomous Database administrative password must be at least 12 characters."
  }
}

variable "compute_count" {
  description = "Approved ECPU compute count for the workshop database."
  type        = number
  default     = 2
}

variable "data_storage_size_in_tbs" {
  description = "Approved storage size in TB for the workshop database."
  type        = number
  default     = 1
}

variable "db_name" {
  description = "Database name."
  type        = string
}

variable "display_name" {
  description = "Autonomous Database display name."
  type        = string
}

variable "db_version" {
  description = "Target Oracle AI Database version; validate availability in the target region before apply."
  type        = string
  default     = "26ai"
}

variable "is_auto_scaling_enabled" {
  description = "Allow CPU autoscaling when explicitly approved."
  type        = bool
  default     = false
}

variable "is_mtls_connection_required" {
  description = "Require mTLS wallets for database connectivity."
  type        = bool
  default     = true
}

variable "license_model" {
  description = "Approved OCI Autonomous Database license model."
  type        = string
  default     = "LICENSE_INCLUDED"
}

variable "freeform_tags" {
  description = "Freeform tags applied to the Autonomous Database."
  type        = map(string)
  default     = {}
}
