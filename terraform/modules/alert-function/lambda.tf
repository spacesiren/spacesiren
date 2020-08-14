module "lambda_function" {
  source = "../lambda-function"

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  description            = var.description
  environment            = merge(var.environment, { APP_NAME = var.app_name })
  functions_bucket       = var.functions_bucket
  name                   = var.name
  role_name              = aws_iam_role.this.name
  role_arn               = aws_iam_role.this.arn
  tags                   = var.tags
  type                   = "alert"
}

resource "aws_lambda_permission" "this" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}

resource "aws_sns_topic_subscription" "alert_function_email" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.function_arn
}
