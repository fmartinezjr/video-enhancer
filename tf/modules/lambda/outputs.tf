output "function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.s3_to_batch.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.s3_to_batch.arn
}
