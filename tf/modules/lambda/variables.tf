variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "batch_job_queue_arn" {
  description = "ARN of the Batch job queue"
  type        = string
}

variable "batch_job_definition_arn" {
  description = "ARN of the Batch job definition"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}
