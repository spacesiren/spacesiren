resource "aws_sns_topic" "alert_honey_token_event" {
  name = "${var.app_name}-alert-honey-token-event"
}

locals {
  # Count flags
  email_enabled     = length(var.alert_email_from_user) > 0 && length(var.alert_email_to_address) > 0 ? 1 : 0
  email_verify_to   = length(var.alert_email_from_user) > 0 && length(var.alert_email_to_address) > 0 && var.alert_email_verify_to_address ? 1 : 0
  pagerduty_enabled = length(var.alert_pagerduty_integration_key) > 0 ? 1 : 0
  slack_enabled     = length(var.alert_slack_webhook_url) > 0 ? 1 : 0

  # Strings
  email_from_domain  = trimsuffix(data.aws_route53_zone.this.name, ".")
  email_from_address = "${var.alert_email_from_user}@${trimsuffix(data.aws_route53_zone.this.name, ".")}"
}

#================================================
# Email
#================================================
resource "aws_ses_domain_identity" "alert_email_from" {
  count  = local.email_enabled
  domain = local.email_from_domain
}

resource "aws_route53_record" "alert_email_from_verification" {
  count   = local.email_enabled
  zone_id = data.aws_route53_zone.this.id
  name    = "_amazonses.${local.email_from_domain}"
  type    = "TXT"
  ttl     = "300"
  records = [aws_ses_domain_identity.alert_email_from[count.index].verification_token]
}

resource "aws_ses_domain_dkim" "alert_email_from" {
  count  = local.email_enabled
  domain = aws_ses_domain_identity.alert_email_from[count.index].domain
}

resource "aws_route53_record" "alert_email_from_dkim" {
  count   = local.email_enabled * 3
  zone_id = data.aws_route53_zone.this.id
  name    = "${aws_ses_domain_dkim.alert_email_from[0].dkim_tokens[count.index]}._domainkey.${local.email_from_domain}"
  type    = "CNAME"
  ttl     = "300"
  records = ["${aws_ses_domain_dkim.alert_email_from[0].dkim_tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_ses_email_identity" "alert_email_to" {
  count = local.email_verify_to
  email = var.alert_email_to_address
}

data "aws_iam_policy_document" "alert_email_function" {
  count = local.email_enabled

  statement {
    effect    = "Allow"
    actions   = ["ses:SendEmail"]
    resources = ["*"]

    condition {
      test     = "StringLike"
      variable = "ses:FromAddress"
      values   = [local.email_from_address]
    }
  }
}

module "alert_email_function" {
  count  = local.email_enabled
  source = "./modules/alert-function"

  name        = "email"
  description = "Handles outgoing alerts for email."
  policy_json = data.aws_iam_policy_document.alert_email_function[count.index].json

  environment = {
    ALERT_EMAIL_FROM_ADDRESS = local.email_from_address
    ALERT_EMAIL_FROM_DISPLAY = var.alert_email_from_display
    ALERT_EMAIL_TO_ADDRESS   = var.alert_email_to_address
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  functions_bucket       = data.aws_s3_bucket.functions.id
  lambda_role_policy     = data.aws_iam_policy_document.lambda_assume_role_policy.json
  sns_topic_arn          = aws_sns_topic.alert_honey_token_event.arn
  tags                   = var.default_tags
}

#================================================
# PagerDuty
#================================================
resource "aws_ssm_parameter" "alert_pagerduty_key" {
  count       = local.pagerduty_enabled
  name        = "/${var.app_name}/alert/pagerduty/integration_key"
  description = "PagerDuty integration key."
  type        = "SecureString"
  value       = var.alert_pagerduty_integration_key
}

data "aws_iam_policy_document" "alert_pagerduty_function" {
  count = local.pagerduty_enabled

  statement {
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = [aws_ssm_parameter.alert_pagerduty_key[count.index].arn]
  }
}

module "alert_pagerduty_function" {
  count  = local.pagerduty_enabled
  source = "./modules/alert-function"

  name        = "pagerduty"
  description = "Handles outgoing alerts for PagerDuty."
  policy_json = data.aws_iam_policy_document.alert_pagerduty_function[count.index].json

  environment = {
    SSM_PATH_PAGERDUTY_INTEGRATION_KEY = aws_ssm_parameter.alert_pagerduty_key[count.index].name
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  functions_bucket       = data.aws_s3_bucket.functions.id
  lambda_role_policy     = data.aws_iam_policy_document.lambda_assume_role_policy.json
  sns_topic_arn          = aws_sns_topic.alert_honey_token_event.arn
  tags                   = var.default_tags
}

#================================================
# Slack
#================================================
resource "aws_ssm_parameter" "alert_slack_webhook" {
  count       = local.slack_enabled
  name        = "/${var.app_name}/alert/slack/webhook_url"
  description = "Slack incoming webhook URL."
  type        = "SecureString"
  value       = var.alert_slack_webhook_url
}

data "aws_iam_policy_document" "alert_slack_function" {
  count = local.slack_enabled
  statement {
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = [aws_ssm_parameter.alert_slack_webhook[count.index].arn]
  }
}

module "alert_slack_function" {
  count  = local.slack_enabled
  source = "./modules/alert-function"

  name        = "slack"
  description = "Handles outgoing alerts for Slack."
  policy_json = data.aws_iam_policy_document.alert_slack_function[count.index].json

  environment = {
    SSM_PATH_SLACK_WEBHOOK_URL = aws_ssm_parameter.alert_slack_webhook[count.index].name
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  functions_bucket       = data.aws_s3_bucket.functions.id
  lambda_role_policy     = data.aws_iam_policy_document.lambda_assume_role_policy.json
  sns_topic_arn          = aws_sns_topic.alert_honey_token_event.arn
  tags                   = var.default_tags
}
