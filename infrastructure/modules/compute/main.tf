################################################################################
# ECS Cluster
#
# Provides the container orchestration layer for:
# - FastAPI backend service
# - Typesense search service
#
# Security:
# - Container Insights enabled
# - ECS Exec enabled
# - CloudWatch logging encrypted with KMS
################################################################################

resource "aws_ecs_cluster" "main" {

  name = "${var.app_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"

      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_exec.name
      }
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cluster"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

################################################################################
# ECS Exec CloudWatch Log Group
################################################################################

resource "aws_cloudwatch_log_group" "ecs_exec" {

  name = "/ecs/${var.app_name}-${var.environment}/exec"

  retention_in_days = 365
  kms_key_id        = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-ecs-exec-logs"
    }
  )
}

################################################################################
# ECR Repository - FastAPI Container Images
#
# Security:
# - Immutable image tags
# - Scan images on push
# - KMS encryption
################################################################################

resource "aws_ecr_repository" "fastapi" {

  name = "${var.app_name}/api"

  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = var.kms_key_arn
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-ecr"
      Environment = var.environment
    }
  )
}

################################################################################
# ECR Lifecycle Policy
#
# Keeps the repository clean by removing unused images.
################################################################################

resource "aws_ecr_lifecycle_policy" "fastapi" {

  repository = aws_ecr_repository.fastapi.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Remove old images"

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }

        action = {
          type = "expire"
        }
      }
    ]
  })
}

################################################################################
# AWS Cloud Map Private DNS Namespace
#
# Used for internal ECS service discovery:
#
# FastAPI ---> typesense.crowncorridor.internal
#
################################################################################

resource "aws_service_discovery_private_dns_namespace" "internal" {

  name        = "${var.app_name}.internal"
  description = "Private namespace for internal ECS services"

  vpc = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-service-discovery"
    }
  )
}

################################################################################
# Typesense Service Discovery Registration
################################################################################

resource "aws_service_discovery_service" "typesense" {

  name = "typesense"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.internal.id
    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-typesense-discovery"
    }
  )
}

################################################################################
# Amazon EFS File System for Typesense Persistent Storage
#
# Security:
# - Encryption enabled using customer-managed KMS key
# - Private subnet mount targets
# - Encrypted transit between ECS and EFS
################################################################################

resource "aws_efs_file_system" "typesense" {

  creation_token = "${var.app_name}-${var.environment}-typesense-efs"

  encrypted        = true
  kms_key_id       = var.kms_key_arn
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-typesense-efs"
      Environment = var.environment
    }
  )
}

################################################################################
# EFS Mount Targets
#
# Creates mount targets in all private subnets.
################################################################################

resource "aws_efs_mount_target" "typesense" {

  count = length(var.private_subnet_ids)

  file_system_id = aws_efs_file_system.typesense.id

  subnet_id = var.private_subnet_ids[count.index]

  security_groups = [
    var.efs_sg_id
  ]

}

################################################################################
# Typesense CloudWatch Logs
################################################################################

resource "aws_cloudwatch_log_group" "typesense" {

  name = "/ecs/${var.app_name}-${var.environment}-typesense"

  retention_in_days = 365
  kms_key_id        = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-typesense-logs"
    }
  )
}

################################################################################
# Typesense ECS Task Definition
#
# Runs Typesense search engine on AWS Fargate.
#
# Security:
# - No public IP
# - Read-only root filesystem
# - Secrets Manager integration
# - Encrypted EFS storage
################################################################################

resource "aws_ecs_task_definition" "typesense" {

  family = "${var.app_name}-${var.environment}-typesense"

  network_mode = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  cpu                = 512
  memory             = 1024
  execution_role_arn = var.ecs_execution_role_arn
  task_role_arn      = var.ecs_task_role_arn

  volume {
    name = "typesense-data"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.typesense.id
      root_directory     = "/"
      transit_encryption = "ENABLED"
    }
  }

  container_definitions = jsonencode(
    [
      {
        name                   = "typesense"
        image                  = "typesense/typesense:26.0"
        essential              = true
        user                   = "1000:1000"
        initProcessEnabled     = true
        readonlyRootFilesystem = true
        portMappings = [
          {
            containerPort = 8108
            hostPort      = 8108
            protocol      = "tcp"
          }
        ]
        environment = [
          {
            name  = "TYPESENSE_DATA_DIR"
            value = "/data"
          }
        ]
        secrets = [
          {
            name      = "TYPESENSE_API_KEY"
            valueFrom = var.typesense_api_key_secret_arn
          }
        ]
        mountPoints = [
          {
            containerPath = "/data"
            sourceVolume  = "typesense-data"
          }
        ]
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group  = aws_cloudwatch_log_group.typesense.name
            awslogs-region = var.aws_region

            awslogs-stream-prefix = "typesense"

          }

        }

      }

    ]
  )

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-typesense-task"
    }
  )

}

################################################################################
# Typesense ECS Service
################################################################################

resource "aws_ecs_service" "typesense" {

  name = "${var.app_name}-${var.environment}-typesense"

  cluster = aws_ecs_cluster.main.id

  task_definition = aws_ecs_task_definition.typesense.arn

  desired_count = 1

  launch_type = "FARGATE"

  deployment_minimum_healthy_percent = 100

  deployment_maximum_percent = 200

  network_configuration {

    subnets = var.private_subnet_ids

    security_groups = [
      var.typesense_sg_id
    ]

    assign_public_ip = false

  }

  service_registries {

    registry_arn = aws_service_discovery_service.typesense.arn

  }

  depends_on = [

    aws_efs_mount_target.typesense

  ]

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-typesense-service"
    }
  )

}

################################################################################
# Application Load Balancer
#
# Public entry point for FastAPI backend.
#
# Security:
# - HTTP/2 enabled
# - Invalid headers dropped
# - Deletion protection enabled
# - Access logging enabled
# - Protected by AWS WAF
################################################################################

resource "aws_lb" "alb" {

  name = "${var.app_name}-${var.environment}-alb"

  internal = false

  load_balancer_type = "application"

  security_groups = [
    var.fastapi_sg_id
  ]

  subnets = var.public_subnet_ids

  enable_http2 = true

  drop_invalid_header_fields = true

  enable_deletion_protection = true

  access_logs {

    bucket = aws_s3_bucket.alb_logs.id

    enabled = true

  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-alb"
      Environment = var.environment
    }
  )

}

################################################################################
# ALB Target Group - FastAPI
################################################################################

resource "aws_lb_target_group" "fastapi" {

  name = "${var.app_name}-${var.environment}-tg"

  port = 8000

  protocol = "HTTP"

  vpc_id = var.vpc_id

  target_type = "ip"

  deregistration_delay = 30

  health_check {

    enabled = true

    path = "/health"

    protocol = "HTTP"

    matcher = "200"

    interval = 30

    timeout = 5

    healthy_threshold = 2

    unhealthy_threshold = 3

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-fastapi-target-group"
    }
  )

}

################################################################################
# HTTP Listener
#
# Redirects all HTTP traffic to HTTPS.
################################################################################

resource "aws_lb_listener" "http" {

  load_balancer_arn = aws_lb.alb.arn

  port     = 80
  protocol = "HTTP"

  default_action {

    type = "redirect"

    redirect {

      port = "443"

      protocol = "HTTPS"

      status_code = "HTTP_301"

    }

  }

}

################################################################################
# HTTPS Listener
#
# Security:
# - TLS 1.2+
# - Strong AWS managed cipher policy
################################################################################

resource "aws_lb_listener" "https" {

  count = var.acm_cert_arn != "" ? 1 : 0

  load_balancer_arn = aws_lb.alb.arn

  port = 443

  protocol = "HTTPS"

  ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  certificate_arn = var.acm_cert_arn

  default_action {

    type = "forward"

    target_group_arn = aws_lb_target_group.fastapi.arn

  }

}

################################################################################
# Attach AWS WAF Web ACL to ALB
#
# Protects public API traffic against:
# - OWASP attacks
# - SQL injection
# - Common exploits
################################################################################

resource "aws_wafv2_web_acl_association" "alb" {
  count = var.waf_web_acl_arn != "" ? 1 : 0

  resource_arn = aws_lb.alb.arn

  web_acl_arn = var.waf_web_acl_arn

}

################################################################################
# ALB Access Logs Bucket
################################################################################

resource "aws_s3_bucket" "alb_logs" {

  bucket = "${var.app_name}-${var.environment}-alb-logs"

  force_destroy = var.environment == "dev" ? true : false

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-alb-logs"
      Environment = var.environment
    }
  )

}

################################################################################
# Block Public Access for ALB Logs
################################################################################

resource "aws_s3_bucket_public_access_block" "alb_logs" {

  bucket                  = aws_s3_bucket.alb_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

################################################################################
# ALB Logs Encryption
################################################################################

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {

  bucket = aws_s3_bucket.alb_logs.id

  rule {

    apply_server_side_encryption_by_default {

      kms_master_key_id = var.kms_key_arn
      sse_algorithm     = "aws:kms"

    }

    bucket_key_enabled = true

  }

}

################################################################################
# ALB Logs Versioning
################################################################################

resource "aws_s3_bucket_versioning" "alb_logs" {

  bucket = aws_s3_bucket.alb_logs.id

  versioning_configuration {

    status = "Enabled"

  }

}

################################################################################
# ALB Logs Lifecycle Policy
#
# Retains logs for 365 days.
################################################################################

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "alb-log-retention"
    status = "Enabled"

    expiration {
      days = 365
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

################################################################################
# ALB Bucket Policy
#
# Allows AWS ELB service to write logs.
# Enforces TLS-only access.
################################################################################

resource "aws_s3_bucket_policy" "alb_logs" {

  bucket = aws_s3_bucket.alb_logs.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AllowELBAccessLogs"

        Effect = "Allow"

        Principal = {

          Service = "logdelivery.elasticloadbalancing.amazonaws.com"

        }

        Action = [

          "s3:PutObject"

        ]

        Resource = "${aws_s3_bucket.alb_logs.arn}/*"

      },

      {

        Sid = "DenyHTTP"

        Effect = "Deny"

        Principal = "*"

        Action = "s3:*"

        Resource = [

          aws_s3_bucket.alb_logs.arn,

          "${aws_s3_bucket.alb_logs.arn}/*"

        ]

        Condition = {

          Bool = {

            "aws:SecureTransport" = "false"

          }

        }

      }

    ]

  })

}

################################################################################
# FastAPI CloudWatch Log Group
#
# Application logs are encrypted with customer-managed KMS key.
################################################################################

resource "aws_cloudwatch_log_group" "fastapi" {

  name = "/ecs/${var.app_name}-${var.environment}-fastapi"

  retention_in_days = 365

  kms_key_id = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-fastapi-logs"
    }
  )

}

################################################################################
# FastAPI ECS Task Definition
#
# Runs the backend API service.
#
# Security:
# - Private networking
# - Secrets Manager integration
# - Read-only filesystem
# - Non-root execution support
# - Encrypted CloudWatch logs
################################################################################

resource "aws_ecs_task_definition" "fastapi" {

  family = "${var.app_name}-${var.environment}-fastapi"

  network_mode = "awsvpc"

  requires_compatibilities = [

    "FARGATE"

  ]

  cpu = 512

  memory = 1024

  execution_role_arn = var.ecs_execution_role_arn

  task_role_arn = var.ecs_task_role_arn

  runtime_platform {

    operating_system_family = "LINUX"

    cpu_architecture = "X86_64"

  }

  container_definitions = jsonencode(

    [

      {

        name = "fastapi"

        image = "${aws_ecr_repository.fastapi.repository_url}:${var.image_tag}"

        essential = true

        initProcessEnabled = true

        readonlyRootFilesystem = true

        portMappings = [

          {

            containerPort = 8000

            hostPort = 8000

            protocol = "tcp"

          }

        ]

        environment = [

          {

            name = "ENVIRONMENT"

            value = var.environment

          },

          {

            name = "TYPESENSE_HOST"

            value = "typesense.${var.app_name}.internal"

          },

          {

            name = "TYPESENSE_PORT"

            value = "8108"

          },

          {

            name = "TYPESENSE_PROTOCOL"

            value = "http"

          }

        ]

        secrets = [

          {

            name = "TYPESENSE_API_KEY"

            valueFrom = var.typesense_api_key_secret_arn

          },

          {

            name = "DATABASE_CREDENTIALS"

            valueFrom = var.db_secret_arn

          }

        ]

        logConfiguration = {

          logDriver = "awslogs"

          options = {

            awslogs-group = aws_cloudwatch_log_group.fastapi.name

            awslogs-region = var.aws_region

            awslogs-stream-prefix = "fastapi"

          }

        }

      }

    ]

  )

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-fastapi-task"
    }
  )

}

################################################################################
# FastAPI ECS Service
#
# Runs FastAPI behind Application Load Balancer.
################################################################################

resource "aws_ecs_service" "fastapi" {

  name = "${var.app_name}-${var.environment}-fastapi"

  cluster = aws_ecs_cluster.main.id

  task_definition = aws_ecs_task_definition.fastapi.arn

  desired_count = 2

  launch_type = "FARGATE"

  deployment_minimum_healthy_percent = 100

  deployment_maximum_percent = 200

  enable_execute_command = true

  health_check_grace_period_seconds = 60

  network_configuration {

    subnets = var.private_subnet_ids

    security_groups = [

      var.fastapi_sg_id

    ]

    assign_public_ip = false

  }

  load_balancer {

    target_group_arn = aws_lb_target_group.fastapi.arn

    container_name = "fastapi"

    container_port = 8000

  }

  depends_on = [

    aws_lb_listener.http

  ]

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-fastapi-service"
    }
  )

}

################################################################################
# ECS Service Auto Scaling Target
#
# Allows production workloads to scale automatically.
################################################################################

resource "aws_appautoscaling_target" "fastapi" {

  max_capacity = var.fastapi_max_capacity

  min_capacity = var.fastapi_min_capacity

  resource_id = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.fastapi.name}"

  scalable_dimension = "ecs:service:DesiredCount"

  service_namespace = "ecs"

}

################################################################################
# CPU Based Scaling Policy
################################################################################

resource "aws_appautoscaling_policy" "fastapi_cpu" {

  name = "${var.app_name}-${var.environment}-fastapi-cpu-scaling"

  policy_type = "TargetTrackingScaling"

  resource_id = aws_appautoscaling_target.fastapi.resource_id

  scalable_dimension = aws_appautoscaling_target.fastapi.scalable_dimension

  service_namespace = aws_appautoscaling_target.fastapi.service_namespace

  target_tracking_scaling_policy_configuration {

    predefined_metric_specification {

      predefined_metric_type = "ECSServiceAverageCPUUtilization"

    }

    target_value = 70

    scale_in_cooldown = 300

    scale_out_cooldown = 60

  }

}
