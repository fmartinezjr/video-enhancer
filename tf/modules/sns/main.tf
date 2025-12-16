resource "aws_sns_topic" "video_processing" {
  name = "${var.app_name}-notifications"
  tags = var.tags
}


resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.video_processing.arn
  protocol  = "email"
  endpoint  = var.notification_email
}
