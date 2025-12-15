output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.videos.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.videos.arn
}

output "input_prefix" {
  description = "S3 prefix for input videos"
  value       = "input/"
}

output "output_prefix" {
  description = "S3 prefix for output videos"
  value       = "output/"
}
