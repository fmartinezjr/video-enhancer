variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "notification_email" {
  description = "Email address to receive notifications"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}
