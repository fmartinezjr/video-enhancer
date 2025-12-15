module "ecr" {
  source   = "./modules/ecr"
  app_name = var.app_name
  tags     = var.tags
}