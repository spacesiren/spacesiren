resource "aws_lambda_function" "this" {
  function_name = "${var.app_name}-${var.type}-${var.name}"
  description   = var.description
  runtime       = "python3.8"
  handler       = "${local.filename}.main"
  role          = var.role_arn
  memory_size   = var.memory_size
  timeout       = var.timeout

  environment {
    variables = var.environment
  }

  s3_bucket        = var.functions_bucket
  s3_key           = aws_s3_bucket_object.this.key
  source_code_hash = data.archive_file.this.output_base64sha256

  tags = var.tags
}
