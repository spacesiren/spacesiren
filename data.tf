data "aws_caller_identity" "this" {}

data "aws_region" "this" {}

data "aws_route53_zone" "this" {
  name = var.dns_zone_name
}

data "aws_s3_bucket" "cloudtrail" {
  bucket = var.cloudtrail_bucket
}

data "aws_s3_bucket" "functions" {
  bucket = var.functions_bucket
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}
