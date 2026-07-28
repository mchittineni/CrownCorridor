##############################################
# 1. VPC & Networking Module
##############################################

module "vpc" {

  source = "./modules/vpc"

  app_name    = var.app_name
  environment = var.environment

  vpc_cidr = var.vpc_cidr

  availability_zones = var.availability_zones

  public_subnet_cidrs   = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs

  tags = var.tags
}

##############################################
# 2. Security Foundation Module
#
# Creates:
# - KMS CMK
# - IAM Roles
# - Security Groups
# - CloudTrail
# - GuardDuty
# - Security Hub
##############################################

module "security" {

  source = "./modules/security"

  app_name    = var.app_name
  environment = var.environment

  vpc_id = module.vpc.vpc_id

  vpc_cidr = module.vpc.vpc_cidr_block

  enable_guardduty = true

  enable_securityhub = true

  tags = var.tags

  depends_on = [
    module.vpc
  ]
}

##############################################
# 3. AWS WAF Module
##############################################

module "waf" {

  source = "./modules/waf"

  app_name    = var.app_name
  environment = var.environment

  rate_limit_threshold = 2000

  tags = var.tags
}

##############################################
# 4. CDN Module
#
# Creates:
# - S3 frontend bucket
# - CloudFront Distribution
# - Origin Access Control
##############################################

module "cdn" {

  source = "./modules/cdn"

  app_name    = var.app_name
  environment = var.environment

  kms_key_arn = module.security.kms_key_arn

  waf_web_acl_arn = module.waf.web_acl_arn

  tags = var.tags

  depends_on = [
    module.security,
    module.waf
  ]
}

##############################################
# 5. Cognito Authentication Module
##############################################

module "auth" {

  source = "./modules/auth"

  app_name    = var.app_name
  environment = var.environment

  cognito_domain_prefix = "${var.app_name}-${var.environment}-auth"

  tags = var.tags
}

##############################################
# 6. RDS PostgreSQL + PostGIS Database
##############################################

module "database" {

  source = "./modules/database"

  app_name    = var.app_name
  environment = var.environment

  db_subnet_group_name = module.vpc.db_subnet_group_name

  rds_sg_id = module.security.rds_sg_id

  kms_key_arn = module.security.kms_key_arn

  multi_az = true

  deletion_protection = var.environment == "prod"

  tags = var.tags

  depends_on = [
    module.security,
    module.vpc
  ]
}

##############################################
# 7. Secrets Manager + SSM
##############################################

module "secrets_ssm" {

  source = "./modules/secrets_ssm"

  app_name    = var.app_name
  environment = var.environment

  kms_key_arn = module.security.kms_key_arn

  db_address = module.database.db_address

  db_port = module.database.db_port

  db_name = module.database.db_name

  db_username = module.database.db_username

  db_password = module.database.db_password

  typesense_api_key = var.typesense_api_key

  tags = var.tags

  depends_on = [
    module.database
  ]
}

##############################################
# 8. ECS Compute Module
#
# Creates:
# - ECS Cluster
# - ECS Fargate Services
# - ALB
# - ECR
# - Typesense
# - EFS
##############################################

module "compute" {

  source = "./modules/compute"

  app_name = var.app_name

  environment = var.environment

  vpc_id = module.vpc.vpc_id

  public_subnet_ids = module.vpc.public_subnet_ids

  private_subnet_ids = module.vpc.private_subnet_ids

  ecs_execution_role_arn = module.security.ecs_execution_role_arn

  ecs_task_role_arn = module.security.ecs_task_role_arn

  fastapi_sg_id = module.security.fastapi_sg_id

  typesense_sg_id = module.security.typesense_sg_id

  efs_sg_id = module.security.efs_sg_id

  typesense_api_key_secret_arn = module.secrets_ssm.typesense_key_secret_arn

  db_secret_arn = module.secrets_ssm.db_secret_arn

  kms_key_arn = module.security.kms_key_arn

  acm_cert_arn = var.acm_certificate_arn

  tags = var.tags

  depends_on = [

    module.database,

    module.secrets_ssm

  ]
}

##############################################
# 9. API Gateway HTTP API
##############################################

module "api_gateway" {

  source = "./modules/api_gateway"

  app_name = var.app_name

  environment = var.environment

  cognito_user_pool_id = module.auth.user_pool_id

  cognito_client_id = module.auth.user_pool_client_id

  backend_integration_uri = "https://${module.compute.alb_dns_name}"

  kms_key_arn = module.security.kms_key_arn

  tags = var.tags

  depends_on = [

    module.compute,

    module.auth

  ]

}

##############################################
# 10. EventBridge + SNS Alerting
##############################################

module "events_alerting" {

  source = "./modules/events_alerting"

  app_name = var.app_name

  environment = var.environment

  alert_email = var.alert_email

  kms_key_arn = module.security.kms_key_arn

  tags = var.tags

}
