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

module "batch" {
  source             = "./modules/batch"
  app_name           = var.app_name
  ecr_repository_url = module.ecr.repository_url
  bucket_name        = module.s3.bucket_name
  instance_types     = var.batch_instance_types
  max_vcpus          = var.batch_max_vcpus
  job_vcpus          = var.job_vcpus
  job_memory         = var.job_memory
  region             = var.aws_region
  tags               = var.tags
}