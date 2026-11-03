variable "enabled" {
  description = "Create the private workshop bucket."
  type        = bool
  default     = true
}

variable "compartment_id" {
  description = "Target compartment OCID."
  type        = string
}

variable "namespace" {
  description = "Object Storage namespace."
  type        = string
}

variable "bucket_name" {
  description = "Workshop bucket name."
  type        = string
}

variable "freeform_tags" {
  description = "Freeform tags applied to the bucket."
  type        = map(string)
  default     = {}
}
