#================================================
# API Gateway
#================================================
resource "aws_apigatewayv2_api" "this" {
  name          = var.app_name
  description   = "API for ${var.app_name}"
  protocol_type = "HTTP"
  tags          = var.default_tags
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true
  tags        = var.default_tags

  default_route_settings {
    throttling_burst_limit = var.api_burst_limit
    throttling_rate_limit  = var.api_rate_limit
  }

  lifecycle {
    ignore_changes = [deployment_id]
  }
}

#================================================
# Custom domain
#================================================
resource "aws_acm_certificate" "api" {
  domain_name       = "api.${data.aws_route53_zone.this.name}"
  validation_method = "DNS"
  tags              = var.default_tags

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "acm_validation_api" {
  for_each = {
    for dvo in aws_acm_certificate.api.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id         = data.aws_route53_zone.this.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 60
  allow_overwrite = true
}

//resource "aws_acm_certificate_validation" "api" {
//  certificate_arn         = aws_acm_certificate.api.arn
//  validation_record_fqdns = [aws_route53_record.acm_validation_api.fqdn]
//}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.acm_validation_api : record.fqdn]
}

resource "aws_apigatewayv2_domain_name" "this" {
  domain_name = "api.${data.aws_route53_zone.this.name}"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.api.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = aws_apigatewayv2_domain_name.this.domain_name
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.this.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.this.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = true
  }
}

resource "aws_apigatewayv2_api_mapping" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  domain_name = aws_apigatewayv2_domain_name.this.id
  stage       = aws_apigatewayv2_stage.this.id
}

#================================================
# Key API function and endpoints
#================================================
resource "random_password" "provision_key" {
  length  = 64
  special = false
}

resource "aws_ssm_parameter" "provision_key" {
  name  = "/${var.app_name}/api/provision_key"
  type  = "SecureString"
  value = random_password.provision_key.result
}


resource "aws_iam_role" "api_key" {
  name               = "${var.app_name}-lambda-api-key"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_function_api_key" {
  statement {
    effect    = "Allow"
    resources = [aws_dynamodb_table.api_keys.arn]

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan"
    ]
  }

  statement {
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = [aws_ssm_parameter.provision_key.arn]
  }
}

resource "aws_iam_policy" "api_key" {
  name   = "${var.app_name}-lambda-api-key"
  policy = data.aws_iam_policy_document.lambda_function_api_key.json
}

resource "aws_iam_role_policy_attachment" "api_key" {
  role       = aws_iam_role.api_key.name
  policy_arn = aws_iam_policy.api_key.arn
}

module "lambda_function_api_key" {
  source = "./modules/lambda-function"

  type             = "api"
  name             = "key"
  description      = "Handles /key API requests"
  functions_bucket = data.aws_s3_bucket.functions.id
  role_name        = aws_iam_role.api_key.name
  role_arn         = aws_iam_role.api_key.arn
  memory_size      = 256
  timeout          = 60

  environment = {
    APP_NAME = var.app_name
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  tags                   = var.default_tags
}

resource "aws_lambda_permission" "api_key" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function_api_key.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/*/key"
}

resource "aws_apigatewayv2_integration" "api_key" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.lambda_function_api_key.invoke_arn
  payload_format_version = "2.0"

  lifecycle {
    ignore_changes = [passthrough_behavior]
  }
}

resource "aws_apigatewayv2_route" "api_key_get" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /key"
  target    = "integrations/${aws_apigatewayv2_integration.api_key.id}"
}

resource "aws_apigatewayv2_route" "api_key_post" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /key"
  target    = "integrations/${aws_apigatewayv2_integration.api_key.id}"
}

resource "aws_apigatewayv2_route" "api_key_patch" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "PATCH /key"
  target    = "integrations/${aws_apigatewayv2_integration.api_key.id}"
}

resource "aws_apigatewayv2_route" "api_key_delete" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "DELETE /key"
  target    = "integrations/${aws_apigatewayv2_integration.api_key.id}"
}

#================================================
# Honey token API function and endpoints
#================================================
resource "aws_iam_role" "api_token" {
  name               = "${var.app_name}-lambda-api-token"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_function_api_token" {
  statement {
    effect    = "Allow"
    resources = [aws_dynamodb_table.api_keys.arn]

    actions = [
      "dynamodb:GetItem"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:Scan",
      "dynamodb:Query",
    ]

    resources = [
      aws_dynamodb_table.honey_tokens.arn,
      aws_dynamodb_table.iam_users.arn,
      "${aws_dynamodb_table.events.arn}/index/AccessKeyID-EventTime",
      "${aws_dynamodb_table.iam_users.arn}/index/NumTokens",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
    ]

    resources = [
      aws_dynamodb_table.events.arn,
      "${aws_dynamodb_table.events.arn}/index/AccessKeyID-EventTime",
    ]
  }

  statement {
    effect    = "Allow"
    resources = ["*"]

    actions = [
      "iam:CreateUser",
      "iam:DeleteUser",
      "iam:TagUser",
      "iam:CreateAccessKey",
      "iam:DeleteAccessKey"
    ]

    condition {
      test     = "StringLike"
      variable = "iam:ResourceTag/${var.app_name}-honey-user"
      values   = ["true"]
    }
  }

  statement {
    effect = "Allow"

    actions = [
      "iam:AddUserToGroup",
      "iam:RemoveUserFromGroup",
    ]

    resources = [
      aws_iam_group.honey_users.arn,
      "arn:aws:iam::*:user/*"
    ]
  }
}

resource "aws_iam_policy" "api_token" {
  name   = "${var.app_name}-lambda-api-token"
  policy = data.aws_iam_policy_document.lambda_function_api_token.json
}

resource "aws_iam_role_policy_attachment" "api_token" {
  role       = aws_iam_role.api_token.name
  policy_arn = aws_iam_policy.api_token.arn
}

module "lambda_function_api_token" {
  source = "./modules/lambda-function"

  type             = "api"
  name             = "token"
  description      = "Handles /token API requests"
  functions_bucket = data.aws_s3_bucket.functions.id
  role_name        = aws_iam_role.api_token.name
  role_arn         = aws_iam_role.api_token.arn
  memory_size      = 256
  timeout          = 60

  environment = {
    APP_NAME = var.app_name
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  tags                   = var.default_tags
}

resource "aws_lambda_permission" "api_token" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function_api_token.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/*/token"
}

resource "aws_apigatewayv2_integration" "api_token" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.lambda_function_api_token.invoke_arn
  payload_format_version = "2.0"

  lifecycle {
    ignore_changes = [passthrough_behavior]
  }
}

resource "aws_apigatewayv2_route" "api_token_get" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /token"
  target    = "integrations/${aws_apigatewayv2_integration.api_token.id}"
}

resource "aws_apigatewayv2_route" "api_token_post" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "POST /token"
  target    = "integrations/${aws_apigatewayv2_integration.api_token.id}"
}

resource "aws_apigatewayv2_route" "api_token_patch" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "PATCH /token"
  target    = "integrations/${aws_apigatewayv2_integration.api_token.id}"
}

resource "aws_apigatewayv2_route" "api_token_delete" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "DELETE /token"
  target    = "integrations/${aws_apigatewayv2_integration.api_token.id}"
}

#================================================
# Honey events API function and endpoints
#================================================
resource "aws_iam_role" "api_event" {
  name               = "${var.app_name}-lambda-api-event"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_function_api_event" {
  statement {
    effect    = "Allow"
    resources = [aws_dynamodb_table.api_keys.arn]

    actions = [
      "dynamodb:GetItem"
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:GetItem",
      "dynamodb:Query"
    ]

    resources = [
      aws_dynamodb_table.events.arn,
      aws_dynamodb_table.honey_tokens.arn,
      aws_dynamodb_table.iam_users.arn,
      "${aws_dynamodb_table.events.arn}/index/AccessKeyID-EventTime"
    ]
  }
}

resource "aws_iam_policy" "api_event" {
  name   = "${var.app_name}-lambda-api-event"
  policy = data.aws_iam_policy_document.lambda_function_api_event.json
}

resource "aws_iam_role_policy_attachment" "api_event" {
  role       = aws_iam_role.api_event.name
  policy_arn = aws_iam_policy.api_event.arn
}

module "lambda_function_api_event" {
  source = "./modules/lambda-function"

  type             = "api"
  name             = "event"
  description      = "Handles /event API requests"
  functions_bucket = data.aws_s3_bucket.functions.id
  role_name        = aws_iam_role.api_event.name
  role_arn         = aws_iam_role.api_event.arn
  memory_size      = 256
  timeout          = 60

  environment = {
    APP_NAME = var.app_name
  }

  app_name               = var.app_name
  cloudwatch_expire_days = var.cloudwatch_expire_days
  tags                   = var.default_tags
}

resource "aws_lambda_permission" "api_event" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function_api_event.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/*/event"
}

resource "aws_apigatewayv2_integration" "api_event" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = module.lambda_function_api_event.invoke_arn
  payload_format_version = "2.0"

  lifecycle {
    ignore_changes = [passthrough_behavior]
  }
}

resource "aws_apigatewayv2_route" "api_event_get" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "GET /event"
  target    = "integrations/${aws_apigatewayv2_integration.api_event.id}"
}
