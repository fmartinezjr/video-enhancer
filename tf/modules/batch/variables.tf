variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository"
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "instance_types" {
  description = "EC2 instance types for Batch compute environment"
  type        = list(string)
}

variable "max_vcpus" {
  description = "Maximum vCPUs for Batch compute environment"
  type        = number
}

variable "job_vcpus" {
  description = "vCPUs allocated per job"
  type        = number
}

variable "job_memory" {
  description = "Memory (MB) allocated per job"
  type        = number
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}
