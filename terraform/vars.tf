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

# Pushover
variable "alert_pushover_user_key" {
  description = "User or group key for Pushover alerts."
  type        = string
  default     = ""
}

variable "alert_pushover_api_key" {
  description = "API (application) key for Pushover alerts."
  type        = string
  default     = ""
}

variable "alert_pushover_priority" {
  description = "Priority level for Pushover alerts. -2 = lowest, 2 = highest."
  type        = number
  default     = 0

  validation {
    condition = (
      var.alert_pushover_priority >= -2 &&
      var.alert_pushover_priority <= 2
    )
    error_message = "The value for alert_pushover_priority must be between -2 and 2."
  }
}

variable "alert_pushover_emergency_retry" {
  description = "Interval in seconds to retry an emergency (priority 2) notification for Pushover alerts."
  type        = number
  default     = 300

  validation {
    condition = (
      var.alert_pushover_emergency_retry >= 30 &&
      var.alert_pushover_emergency_retry <= 10800
    )
    error_message = "The value for alert_pushover_emergency_retry must be between 30 and 10800."
  }
}

variable "alert_pushover_emergency_expire" {
  description = "Time in seconds to stop retrying an emergency (priority 2) notification for Pushover alerts."
  type        = number
  default     = 10800

  validation {
    condition = (
      var.alert_pushover_emergency_expire >= 0 &&
      var.alert_pushover_emergency_expire <= 10800
    )
    error_message = "The value for alert_pushover_emergency_expire must be between 0 and 10800."
  }
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
