resource "aws_dynamodb_table" "api_keys" {
  name         = "${var.app_name}-api-keys"
  hash_key     = "KeyID"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "KeyID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = var.default_tags
}

resource "aws_dynamodb_table" "events" {
  name         = "${var.app_name}-events"
  hash_key     = "EventID"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "EventID"
    type = "S"
  }

  attribute {
    name = "EventTime"
    type = "N"
  }

  attribute {
    name = "AccessKeyID"
    type = "S"
  }

  global_secondary_index {
    name            = "AccessKeyID-EventTime"
    hash_key        = "AccessKeyID"
    range_key       = "EventTime"
    projection_type = "ALL"
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = var.default_tags
}

resource "aws_dynamodb_table" "iam_users" {
  name         = "${var.app_name}-iam-users"
  hash_key     = "Username"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "Username"
    type = "S"
  }

  attribute {
    name = "NumTokens"
    type = "N"
  }

  global_secondary_index {
    name            = "NumTokens"
    hash_key        = "NumTokens"
    projection_type = "INCLUDE"

    non_key_attributes = [
      "AccountID",
      "Username"
    ]
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = var.default_tags
}

resource "aws_dynamodb_table" "honey_tokens" {
  name         = "${var.app_name}-honey-tokens"
  hash_key     = "AccessKeyID"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "AccessKeyID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = var.default_tags
}


