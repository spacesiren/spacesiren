resource "aws_iam_group" "honey_users" {
  name = "${var.app_name}-honey-users"
}

data "aws_iam_policy_document" "honey_users_deny_all" {
  statement {
    effect    = "Deny"
    actions   = ["*"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "honey_users_deny_all" {
  name   = "${var.app_name}-honey-users-deny-all"
  policy = data.aws_iam_policy_document.honey_users_deny_all.json
}

resource "aws_iam_group_policy_attachment" "honey_users_deny_all" {
  group      = aws_iam_group.honey_users.name
  policy_arn = aws_iam_policy.honey_users_deny_all.arn
}