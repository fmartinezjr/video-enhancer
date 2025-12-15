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