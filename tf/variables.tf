variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "notification_email" {
  description = "Email address to receive SNS notifications"
  type        = string
}

variable "batch_instance_types" {
  description = "EC2 instance types for Batch compute environment"
  type        = list(string)
  default     = ["c5.xlarge", "c5.2xlarge"]
}

variable "batch_max_vcpus" {
  description = "Maximum vCPUs for Batch compute environment"
  type        = number
  default     = 16
}

variable "job_vcpus" {
  description = "vCPUs allocated per video processing job"
  type        = number
  default     = 4
}

variable "job_memory" {
  description = "Memory (MB) allocated per video processing job"
  type        = number
  default     = 8192
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}
