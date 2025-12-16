module "ecr" {
  source   = "./modules/ecr"
  app_name = var.app_name
  tags     = var.tags
}

module "s3" {
  source   = "./modules/s3"
  app_name = var.app_name
  tags     = var.tags
}

module "sns" {
  source             = "./modules/sns"
  app_name           = var.app_name
  notification_email = var.notification_email
  tags               = var.tags
}

module "batch" {
  source             = "./modules/batch"
  app_name           = var.app_name
  ecr_repository_url = module.ecr.repository_url
  bucket_name        = module.s3.bucket_name
  sns_topic_arn      = module.sns.topic_arn
  instance_types     = var.batch_instance_types
  max_vcpus          = var.batch_max_vcpus
  job_vcpus          = var.job_vcpus
  job_memory         = var.job_memory
  region             = var.aws_region
  tags               = var.tags
}

module "lambda" {
  source                   = "./modules/lambda"
  app_name                 = var.app_name
  bucket_name              = module.s3.bucket_name
  bucket_arn               = module.s3.bucket_arn
  batch_job_queue_arn      = module.batch.job_queue_arn
  batch_job_definition_arn = module.batch.job_definition_arn
  tags                     = var.tags
}