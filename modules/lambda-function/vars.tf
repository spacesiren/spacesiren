variable "type" {
  type = string
}

variable "name" {
  type = string
}

variable "description" {
  type    = string
  default = ""
}

variable "functions_bucket" {
  type = string
}

variable "role_name" {
  type = string
}

variable "role_arn" {
  type = string
}

variable "memory_size" {
  type    = number
  default = 256
}

variable "timeout" {
  type    = number
  default = 60
}

variable "environment" {
  type = map(string)
  default = {
    PLACEHOLDER = "true"
  }
}

variable "app_name" {
  type = string
}

variable "cloudwatch_expire_days" {
  type = number
}

variable "tags" {
  type = map(string)
}

locals {
  filename = join("_", [var.type, replace(var.name, "-", "_")])
}
