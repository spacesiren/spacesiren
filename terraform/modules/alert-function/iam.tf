resource "aws_iam_role" "this" {
  name               = "${var.app_name}-lambda-alert-${var.name}"
  assume_role_policy = var.lambda_role_policy
}

resource "aws_iam_policy" "this" {
  name   = "${var.app_name}-lambda-alert-${var.name}"
  policy = var.policy_json
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
