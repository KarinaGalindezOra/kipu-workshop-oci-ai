variable "region" {
  type    = string
  default = "us-chicago-1"
}

variable "oci_config_profile" {
  description = "Named OCI session profile available in the standard private OCI config file."
  type        = string
  default     = "KHIPU_MEMORY_OWNER"
}

variable "tenancy_ocid" {
  type = string
}

variable "create_workshop_compartment" {
  type    = bool
  default = true
}

variable "parent_compartment_id" {
  type     = string
  default  = null
  nullable = true
}

variable "existing_compartment_id" {
  type     = string
  default  = null
  nullable = true
}

variable "existing_compartment_name" {
  type     = string
  default  = null
  nullable = true
}

variable "workshop_compartment_name" {
  type    = string
  default = "cmp-khipu-ai-workshop-dev"
}

variable "workshop_compartment_description" {
  type    = string
  default = "Disposable OCI AI workshop pilot for Khipu."
}

variable "object_storage_namespace" {
  type = string
}

variable "workshop_bucket_name" {
  type    = string
  default = "khipu-ai-workshop-assets"
}

variable "enable_object_storage" {
  type    = bool
  default = true
}

variable "enable_autonomous_database" {
  type    = bool
  default = false
}

variable "autonomous_admin_password" {
  type      = string
  sensitive = true
  default   = null
  nullable  = true
}

variable "autonomous_compute_count" {
  type    = number
  default = 2
}

variable "autonomous_storage_tbs" {
  type    = number
  default = 1
}

variable "autonomous_db_name" {
  type    = string
  default = "KHIPUWS"
}

variable "autonomous_display_name" {
  type    = string
  default = "khipu-ai-workshop-adb"
}

variable "autonomous_db_version" {
  type    = string
  default = "26ai"
}

variable "autonomous_auto_scaling_enabled" {
  type    = bool
  default = false
}

variable "autonomous_mtls_required" {
  type    = bool
  default = true
}

variable "autonomous_license_model" {
  type    = string
  default = "LICENSE_INCLUDED"
}

variable "enable_iam_policies" {
  type    = bool
  default = false
}

variable "participant_group_name" {
  type    = string
  default = "khipu-workshop-participants"
}

variable "participant_group_identity_domain" {
  description = "Identity domain containing the participant IAM group."
  type        = string
  default     = "Default"
}

variable "facilitator_group_name" {
  type    = string
  default = "khipu-workshop-facilitators"
}

variable "iam_policy_name" {
  type    = string
  default = "khipu-ai-workshop-policy"
}

variable "freeform_tags" {
  type    = map(string)
  default = {}
}
