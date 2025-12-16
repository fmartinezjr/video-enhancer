resource "aws_iam_role" "batch_service_role" {
  name = "${var.app_name}-batch-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "batch.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "batch_service_role" {
  role       = aws_iam_role.batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.app_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "batch_job_role" {
  name = "${var.app_name}-batch-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "batch_job_s3_policy" {
  name = "${var.app_name}-batch-job-s3"
  role = aws_iam_role.batch_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::*${var.app_name}*",
          "arn:aws:s3:::*${var.app_name}*/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "batch_job_sns_policy" {
  name = "${var.app_name}-batch-job-sns"
  role = aws_iam_role.batch_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = var.sns_topic_arn
      }
    ]
  })
}

# Security group for Batch compute environment
resource "aws_security_group" "batch" {
  name        = "${var.app_name}-batch-sg"
  description = "Security group for Batch compute environment"
  vpc_id      = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_batch_compute_environment" "video_processor" {
  compute_environment_name = "${var.app_name}-compute-env"
  type                     = "MANAGED"
  service_role             = aws_iam_role.batch_service_role.arn

  compute_resources {
    type          = "EC2"
    instance_type = var.instance_types

    min_vcpus     = 0
    max_vcpus     = var.max_vcpus
    desired_vcpus = 0

    subnets            = data.aws_subnets.default.ids
    security_group_ids = [aws_security_group.batch.id]

    instance_role = aws_iam_instance_profile.ecs_instance.arn

    tags = var.tags
  }

  tags = var.tags

  depends_on = [aws_iam_role_policy_attachment.batch_service_role]
}

resource "aws_iam_instance_profile" "ecs_instance" {
  name = "${var.app_name}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

resource "aws_iam_role" "ecs_instance_role" {
  name = "${var.app_name}-ecs-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_batch_job_queue" "video_processor" {
  name     = "${var.app_name}-job-queue"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.video_processor.arn
  }

  tags = var.tags
}

resource "aws_batch_job_definition" "video_processor" {
  name = "${var.app_name}-job-definition"
  type = "container"

  platform_capabilities = ["EC2"]

  container_properties = jsonencode({
    image = "${var.ecr_repository_url}:latest"

    jobRoleArn       = aws_iam_role.batch_job_role.arn
    executionRoleArn = aws_iam_role.ecs_task_execution_role.arn

    resourceRequirements = [
      {
        type  = "VCPU"
        value = tostring(var.job_vcpus)
      },
      {
        type  = "MEMORY"
        value = tostring(var.job_memory)
      }
    ]

    environment = [
      {
        name  = "SNS_TOPIC_ARN"
        value = var.sns_topic_arn
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.batch_jobs.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "batch"
      }
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "batch_jobs" {
  name              = "/aws/batch/${var.app_name}"
  retention_in_days = 7

  tags = var.tags
}
