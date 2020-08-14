data "aws_iam_policy_document" "cloudtrail_bucket" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetBucketAcl"]
    resources = [data.aws_s3_bucket.cloudtrail.arn]

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
  }

  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${data.aws_s3_bucket.cloudtrail.arn}/AWSLogs/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudtrail_bucket" {
  bucket = data.aws_s3_bucket.cloudtrail.id
  policy = data.aws_iam_policy_document.cloudtrail_bucket.json
}

resource "aws_cloudtrail" "this" {
  name                          = var.app_name
  s3_bucket_name                = data.aws_s3_bucket.cloudtrail.id
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_log_file_validation    = true
  sns_topic_name                = aws_sns_topic.task_cloudtrail_event.name
  tags                          = var.default_tags

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  lifecycle {
    ignore_changes = [event_selector]
  }

  depends_on = [
    aws_s3_bucket_policy.cloudtrail_bucket,
    aws_sns_topic_policy.task_cloudtrail_event
  ]
}
