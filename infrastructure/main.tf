# 1. VPC & Networking Module
module "vpc" {
  source      = "./modules/vpc"
  app_name    = var.app_name
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

# 2. Security, KMS, Audit & Compliance Module
module "security" {
  source         = "./modules/security"
  app_name       = var.app_name
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  vpc_cidr       = module.vpc.vpc_cidr_block
  aws_account_id = var.aws_account_id
}

# 3. AWS WAF Web ACL Module
module "waf" {
  source      = "./modules/waf"
  app_name    = var.app_name
  environment = var.environment
}

# 4. S3 & CloudFront CDN Module
module "cdn" {
  source          = "./modules/cdn"
  app_name        = var.app_name
  environment     = var.environment
  kms_key_arn     = module.security.kms_key_arn
  waf_web_acl_arn = module.waf.web_acl_arn
}

# 5. Cognito Authentication Module
module "auth" {
  source      = "./modules/auth"
  app_name    = var.app_name
  environment = var.environment
}

# 6. Database (RDS PostGIS) Module
module "database" {
  source               = "./modules/database"
  app_name             = var.app_name
  environment          = var.environment
  db_subnet_group_name = module.vpc.db_subnet_group_name
  rds_sg_id            = module.security.rds_sg_id
  kms_key_arn          = module.security.kms_key_arn
}

# 7. Secrets Manager & SSM Parameter Store Module
module "secrets_ssm" {
  source            = "./modules/secrets_ssm"
  app_name          = var.app_name
  environment       = var.environment
  kms_key_arn       = module.security.kms_key_arn
  db_address        = module.database.db_address
  db_port           = module.database.db_port
  db_name           = module.database.db_name
  db_username       = module.database.db_username
  db_password       = module.database.db_password
  typesense_api_key = var.typesense_api_key
}

# 8. Compute Module (ECS Fargate FastAPI & Typesense with EFS)
module "compute" {
  source                       = "./modules/compute"
  app_name                     = var.app_name
  environment                  = var.environment
  vpc_id                       = module.vpc.vpc_id
  public_subnet_ids            = module.vpc.public_subnet_ids
  private_subnet_ids           = module.vpc.private_subnet_ids
  ecs_execution_role_arn       = module.security.ecs_execution_role_arn
  ecs_task_role_arn            = module.security.ecs_task_role_arn
  fastapi_sg_id                = module.security.fastapi_sg_id
  typesense_sg_id              = module.security.typesense_sg_id
  efs_sg_id                    = module.security.efs_sg_id
  typesense_api_key_secret_arn = module.secrets_ssm.typesense_key_secret_arn
  db_secret_arn                = module.secrets_ssm.db_secret_arn
  aws_region                   = var.aws_region
}

# 9. Amazon API Gateway HTTP API Module
module "api_gateway" {
  source                  = "./modules/api_gateway"
  app_name                = var.app_name
  environment             = var.environment
  cognito_user_pool_id    = module.auth.user_pool_id
  cognito_client_id       = module.auth.user_pool_client_id
  backend_integration_uri = "http://${module.compute.alb_dns_name}"
}

# 10. EventBridge Cron & SNS Alerting Module
module "events_alerting" {
  source         = "./modules/events_alerting"
  app_name       = var.app_name
  environment    = var.environment
  alert_email    = var.alert_email
  aws_account_id = var.aws_account_id
}
