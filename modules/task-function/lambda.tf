module "lambda_function" {
  source = "../lambda-function"

  type             = "task"
  name             = var.name
  description      = var.description
  functions_bucket = var.functions_bucket
  role_name        = aws_iam_role.this.name
  role_arn         = aws_iam_role.this.arn
  memory_size      = 256
  timeout          = 60

  environment = var.environment

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  tags                   = var.tags
}

resource "aws_lambda_permission" "this" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}

resource "aws_sns_topic_subscription" "this" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_function.function_arn
}
