output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.s3.bucket_name
}

output "input_prefix" {
  description = "S3 prefix for input videos (upload here)"
  value       = "s3://${module.s3.bucket_name}/${module.s3.input_prefix}"
}

output "output_prefix" {
  description = "S3 prefix for output videos (results here)"
  value       = "s3://${module.s3.bucket_name}/${module.s3.output_prefix}"
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}

output "batch_job_queue_name" {
  description = "Name of the Batch job queue"
  value       = module.batch.job_queue_name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "sns_topic_arn" {
  description = "ARN of the SNS notification topic"
  value       = module.sns.topic_arn
}
