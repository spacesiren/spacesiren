data "archive_file" "this" {
  type        = "zip"
  output_path = "${local.pkg_path}/${local.filename}.zip"

  source {
    content  = file("${local.src_path}/app_common.py")
    filename = "app_common.py"
  }

  source {
    content  = file("${local.src_path}/${var.type}_common.py")
    filename = "${var.type}_common.py"
  }

  source {
    content  = file("${local.src_path}/${local.filename}.py")
    filename = "${local.filename}.py"
  }
}

resource "aws_s3_bucket_object" "this" {
  bucket = var.functions_bucket
  source = data.archive_file.this.output_path
  key    = basename(data.archive_file.this.output_path)
  etag   = filemd5(data.archive_file.this.output_path)
  tags   = var.tags
}
