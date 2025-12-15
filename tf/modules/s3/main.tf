resource "aws_s3_bucket" "videos" {
  bucket = "${var.app_name}-${data.aws_caller_identity.current.account_id}"
  tags   = var.tags
}

data "aws_caller_identity" "current" {}

# Block public access
resource "aws_s3_bucket_public_access_block" "videos" {
  bucket = aws_s3_bucket.videos.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
