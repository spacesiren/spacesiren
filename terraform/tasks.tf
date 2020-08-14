#================================================
# CloudTrail event
#================================================
resource "aws_sns_topic" "task_cloudtrail_event" {
  name = "${var.app_name}-task-cloudtrail-event"
  tags = var.default_tags
}


data "aws_iam_policy_document" "lambda_function_task_cloudtrail_event" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${data.aws_s3_bucket.cloudtrail.arn}/*"]
  }

  statement {
    effect  = "Allow"
    actions = ["dynamodb:GetItem"]

    resources = [
      aws_dynamodb_table.honey_tokens.arn,
      aws_dynamodb_table.iam_users.arn
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.events.arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.task_honey_token_event.arn]
  }
}

data "aws_iam_policy_document" "sns_task_cloudtrail_event" {
  statement {
    sid       = "AWSCloudTrailSNSPolicy20150319"
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.task_cloudtrail_event.arn]

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
  }
}

resource "aws_sns_topic_policy" "task_cloudtrail_event" {
  arn    = aws_sns_topic.task_cloudtrail_event.arn
  policy = data.aws_iam_policy_document.sns_task_cloudtrail_event.json
}

module "task_cloudtrail_event_function" {
  source = "./modules/task-function"

  name        = "cloudtrail-event"
  description = "Ingests CloudTrail events via CloudTrail notify."
  policy_json = data.aws_iam_policy_document.lambda_function_task_cloudtrail_event.json

  environment = {
    APP_NAME                  = var.app_name
    HONEY_EVENT_SNS_TOPIC_ARN = aws_sns_topic.task_honey_token_event.arn
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  functions_bucket       = data.aws_s3_bucket.functions.id
  lambda_role_policy     = data.aws_iam_policy_document.lambda_assume_role_policy.json
  sns_topic_arn          = aws_sns_topic.task_cloudtrail_event.arn
  tags                   = var.default_tags
}

#================================================
# Honey token event
#================================================
resource "aws_sns_topic" "task_honey_token_event" {
  name = "${var.app_name}-task-honey-token-event"
  tags = var.default_tags
}

data "aws_iam_policy_document" "lambda_function_task_honey_token_event" {
  statement {
    effect  = "Allow"
    actions = ["dynamodb:GetItem"]
    resources = [
      aws_dynamodb_table.iam_users.arn,
      aws_dynamodb_table.honey_tokens.arn
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:Query"
    ]

    resources = [
      aws_dynamodb_table.events.arn,
      "${aws_dynamodb_table.events.arn}/index/AccessKeyID-EventTime"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.alert_honey_token_event.arn]
  }
}

module "task_honey_token_event_function" {
  source = "./modules/task-function"

  name        = "honey-token-event"
  description = "Invoked when a honey token performs an action."
  policy_json = data.aws_iam_policy_document.lambda_function_task_honey_token_event.json

  environment = {
    APP_NAME                  = var.app_name
    ALERT_COOLDOWN            = var.alert_cooldown
    HONEY_ALERT_SNS_TOPIC_ARN = aws_sns_topic.alert_honey_token_event.arn
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  functions_bucket       = data.aws_s3_bucket.functions.id
  lambda_role_policy     = data.aws_iam_policy_document.lambda_assume_role_policy.json
  sns_topic_arn          = aws_sns_topic.task_honey_token_event.arn
  tags                   = var.default_tags
}
