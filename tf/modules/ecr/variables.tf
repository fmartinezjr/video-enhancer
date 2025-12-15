variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}
