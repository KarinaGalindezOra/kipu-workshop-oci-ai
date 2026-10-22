variable "create_compartment" {
  description = "Create a child workshop compartment. Set false when an approved compartment already exists."
  type        = bool
}

variable "parent_compartment_id" {
  description = "Parent compartment OCID used only when create_compartment is true."
  type        = string
  default     = null
  nullable    = true
}

variable "existing_compartment_id" {
  description = "Existing approved workshop compartment OCID used when create_compartment is false."
  type        = string
  default     = null
  nullable    = true
}

variable "existing_compartment_name" {
  description = "Display name of the existing approved workshop compartment."
  type        = string
  default     = null
  nullable    = true
}

variable "compartment_name" {
  description = "Name for the workshop compartment."
  type        = string
}

variable "description" {
  description = "Workshop compartment description."
  type        = string
}

variable "freeform_tags" {
  description = "Freeform tags applied to the new compartment."
  type        = map(string)
  default     = {}
}

locals {
  compartment_input_is_valid = var.create_compartment ? (
    var.parent_compartment_id != null && var.parent_compartment_id != ""
    ) : (
    var.existing_compartment_id != null && var.existing_compartment_id != "" &&
    var.existing_compartment_name != null && var.existing_compartment_name != ""
  )
}

resource "terraform_data" "validate_compartment_input" {
  input = local.compartment_input_is_valid

  lifecycle {
    precondition {
      condition     = local.compartment_input_is_valid
      error_message = "Provide parent_compartment_id when creating a compartment, or existing_compartment_id and existing_compartment_name when reusing one."
    }
  }
}
