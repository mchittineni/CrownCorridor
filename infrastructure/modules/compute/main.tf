# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cluster"
      Environment = var.environment
    }
  )
}

# ECR Repository for FastAPI
resource "aws_ecr_repository" "fastapi" {
  name                 = "${var.app_name}/api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}

# Cloud Map Private Service Discovery Namespace
resource "aws_service_discovery_private_dns_namespace" "internal" {
  name        = "${var.app_name}.internal"
  description = "Private DNS namespace for internal microservices"
  vpc         = var.vpc_id
}

# Typesense Service Discovery Registration
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

  health_check_custom_config {}
}

# Amazon EFS File System for Typesense Persistent Storage
resource "aws_efs_file_system" "typesense" {
  creation_token = "${var.app_name}-${var.environment}-typesense-efs"
  encrypted      = true

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

# EFS Mount Targets in Private Subnets
resource "aws_efs_mount_target" "typesense" {
  count           = length(var.private_subnet_ids)
  file_system_id  = aws_efs_file_system.typesense.id
  subnet_id       = var.private_subnet_ids[count.index]
  security_groups = [var.efs_sg_id]
}

# Typesense CloudWatch Log Group
resource "aws_cloudwatch_log_group" "typesense" {
  name              = "/ecs/${var.app_name}-${var.environment}-typesense"
  retention_in_days = 30
}

# FastAPI CloudWatch Log Group
resource "aws_cloudwatch_log_group" "fastapi" {
  name              = "/ecs/${var.app_name}-${var.environment}-fastapi"
  retention_in_days = 30
}

# Typesense Task Definition
resource "aws_ecs_task_definition" "typesense" {
  family                   = "${var.app_name}-${var.environment}-typesense"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  volume {
    name = "typesense-data"

    efs_volume_configuration {
      file_system_id = aws_efs_file_system.typesense.id
      root_directory = "/"
    }
  }

  container_definitions = jsonencode([
    {
      name      = "typesense"
      image     = "typesense/typesense:26.0"
      essential = true
      portMappings = [
        {
          containerPort = 8108
          hostPort      = 8108
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "TYPESENSE_DATA_DIR", value = "/data" }
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
          "awslogs-group"         = aws_cloudwatch_log_group.typesense.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "typesense"
        }
      }
    }
  ])
}

# Typesense ECS Service
resource "aws_ecs_service" "typesense" {
  name            = "${var.app_name}-${var.environment}-typesense"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.typesense.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.typesense_sg_id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.typesense.arn
  }

  depends_on = [aws_efs_mount_target.typesense]
}

# Application Load Balancer for FastAPI Backend
resource "aws_lb" "alb" {
  name                       = "${var.app_name}-${var.environment}-alb"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = [var.fastapi_sg_id]
  subnets                    = var.public_subnet_ids
  drop_invalid_header_fields = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-alb"
      Environment = var.environment
    }
  )
}

resource "aws_lb_target_group" "fastapi" {
  name        = "${var.app_name}-${var.environment}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }
}

# FastAPI Task Definition
resource "aws_ecs_task_definition" "fastapi" {
  family                   = "${var.app_name}-${var.environment}-fastapi"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = "${aws_ecr_repository.fastapi.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "TYPESENSE_HOST", value = "typesense.${var.app_name}.internal" },
        { name = "TYPESENSE_PORT", value = "8108" },
        { name = "TYPESENSE_PROTOCOL", value = "http" },
        { name = "ENVIRONMENT", value = var.environment }
      ]
      secrets = [
        {
          name      = "TYPESENSE_API_KEY"
          valueFrom = var.typesense_api_key_secret_arn
        },
        {
          name      = "DATABASE_CREDENTIALS"
          valueFrom = var.db_secret_arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fastapi.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "fastapi"
        }
      }
    }
  ])
}

# FastAPI ECS Service
resource "aws_ecs_service" "fastapi" {
  name            = "${var.app_name}-${var.environment}-fastapi"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.fastapi_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi.arn
    container_name   = "fastapi"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
