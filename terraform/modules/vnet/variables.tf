variable "name" {
  type        = string
  description = "Virtual network name."
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "address_space" {
  type        = string
  description = "CIDR for the whole network."
  validation {
    condition     = can(cidrnetmask(var.address_space))
    error_message = "address_space must be a valid IPv4 CIDR."
  }
}

variable "subnets" {
  description = "Subnets keyed by name. Each gets its own NSG that denies all inbound except allow_rules."
  type = map(object({
    prefix = string
    allow_rules = optional(list(object({
      name     = string
      priority = number
      protocol = string
      port     = string
      source   = string
    })), [])
  }))
}
