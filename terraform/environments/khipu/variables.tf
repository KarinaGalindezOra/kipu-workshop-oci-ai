variable "region" {
  type = string
}

variable "tenancy_ocid" {
  type = string
}

variable "create_workshop_compartment" {
  type    = bool
  default = false
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
  default = "Khipu OCI AI workshop environment."
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
  default = false
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

variable "team_object_access" {
  description = "Optional team-specific Object Storage access. Keep empty unless team groups and prefixes are approved."
  type = map(object({
    group_name    = string
    object_prefix = string
  }))
  default = {}
}

variable "freeform_tags" {
  type    = map(string)
  default = {}
}
