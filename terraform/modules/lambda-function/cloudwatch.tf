resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.app_name}-${var.type}-${var.name}"
  retention_in_days = var.cloudwatch_expire_days
}

data "aws_iam_policy_document" "cloudwatch" {
  statement {
    effect    = "Allow"
    resources = [aws_cloudwatch_log_group.this.arn]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
  }
}

resource "aws_iam_policy" "cloudwatch" {
  name   = "${var.app_name}-lambda-${var.type}-${var.name}-cloudwatch"
  policy = data.aws_iam_policy_document.cloudwatch.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = var.role_name
  policy_arn = aws_iam_policy.cloudwatch.arn
}
