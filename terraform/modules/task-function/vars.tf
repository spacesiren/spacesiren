variable "name" {
  type = string
}

variable "description" {
  type    = string
  default = ""
}

variable "policy_json" {
  type = string
}

variable "environment" {
  type = map(string)
}

variable "app_name" {
  type = string
}

variable "cloudwatch_expire_days" {
  type = number
}

variable "functions_bucket" {
  type = string
}

variable "lambda_role_policy" {
  type = string
}

variable "sns_topic_arn" {
  type = string
}

variable "tags" {
  type = map(string)
}
