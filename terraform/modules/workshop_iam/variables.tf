variable "create_policies" {
  description = "Create reviewed IAM policies in the tenancy root. Keep false until an administrator approves the policy statements."
  type        = bool
  default     = false
}

variable "tenancy_ocid" {
  description = "Tenancy OCID used as the policy container."
  type        = string
}

variable "workshop_compartment_name" {
  description = "Workshop compartment name used in policy statements."
  type        = string
}

variable "participant_group_name" {
  description = "Existing OCI IAM group for workshop participants."
  type        = string
}

variable "facilitator_group_name" {
  description = "Existing OCI IAM group for workshop facilitators."
  type        = string
}

variable "bucket_name" {
  description = "Workshop bucket name used by optional team-scoped object policies."
  type        = string
}

variable "team_object_access" {
  description = "Optional team-specific group and Object Storage prefix mappings. Empty by default, so participants receive no Object Storage permission."
  type = map(object({
    group_name    = string
    object_prefix = string
  }))
  default = {}

  validation {
    condition = alltrue([
      for access in values(var.team_object_access) : (
        length(trimspace(access.group_name)) > 0 &&
        length(trimspace(access.object_prefix)) > 0 &&
        !startswith(access.object_prefix, "/") &&
        !endswith(access.object_prefix, "/")
      )
    ])
    error_message = "Each team object access entry must contain a group name and a relative object prefix without leading or trailing slashes."
  }
}

variable "policy_name" {
  description = "Name for the tenancy-level IAM policy."
  type        = string
}

variable "freeform_tags" {
  description = "Freeform tags applied to the IAM policy."
  type        = map(string)
  default     = {}
}
