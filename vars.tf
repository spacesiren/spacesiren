#================================================
# Required
#================================================
variable "cloudtrail_bucket" {
  description = "S3 bucket for CloudTrail events."
}

variable "functions_bucket" {
  description = "S3 bucket for Lambda functions."
}

variable "dns_zone_name" {
  description = "Name of existing Route53 hosted zone in your SpaceSiren AWS account. It must be properly delegated from the registrar or parent zone."
}

#================================================
# Alerting
#================================================

# Email
variable "alert_email_from_user" {
  description = "The username of the FROM address for email alerts Domain is set in dns_zone_name."
  type        = string
  default     = ""
}

variable "alert_email_from_display" {
  description = "The display name for email alerts."
  type        = string
  default     = "SpaceSiren Alerts"
}

variable "alert_email_to_address" {
  description = "The TO address for email alerts."
  type        = string
  default     = ""
}

variable "alert_email_verify_to_address" {
  description = "Have SES attempt to verify the TO address. May be required without production SES activation."
  type        = bool
  default     = true
}

# PagerDuty
variable "alert_pagerduty_integration_key" {
  description = "Integration key for PagerDuty alerts."
  type        = string
  default     = ""
}

# Slack
variable "alert_slack_webhook_url" {
  description = "Incoming webhook URL for Slack alerts."
  type        = string
  default     = ""
}

#================================================
# Optional
#================================================
variable "alert_cooldown" {
  description = "How long to wait (in seconds) after an alert is triggered to trigger another if the honey token is still in use."
  type        = number
  default     = 1800
}

variable "api_burst_limit" {
  type    = number
  default = 10
}

variable "api_rate_limit" {
  type    = number
  default = 10
}

variable "app_name" {
  type    = string
  default = "spacesiren"
}

variable "cloudwatch_expire_days" {
  description = "Expiration period for CloudWatch log events."
  type        = number
  default     = 30
}

# Reserved tags: Name, <app_name>-honey-user
variable "default_tags" {
  type    = map(string)
  default = {}
}
