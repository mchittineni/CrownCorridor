############################################################
# DATA SOURCES
############################################################

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

############################################################
# AWS KMS CUSTOMER MANAGED KEY
############################################################

resource "aws_kms_key" "main" {

  description = "${var.app_name}-${var.environment} encryption key for RDS, S3, ECS, Secrets Manager, CloudTrail and CloudWatch"

  deletion_window_in_days = 30

  enable_key_rotation = true

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      # Account root administration
      {
        Sid = "EnableAccountAdministration"

        Effect = "Allow"

        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }

        Action = "kms:*"

        Resource = "*"
      },

      # CloudTrail encryption
      {
        Sid = "AllowCloudTrailEncryption"

        Effect = "Allow"

        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }

        Action = [
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]

        Resource = "*"
      },

      # ECS / Secrets Manager / RDS usage
      {
        Sid = "AllowAWSServiceUsage"

        Effect = "Allow"

        Principal = {
          Service = [
            "ecs-tasks.amazonaws.com",
            "secretsmanager.amazonaws.com",
            "rds.amazonaws.com",
            "logs.amazonaws.com"
          ]
        }

        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]

        Resource = "*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-kms-key"
      Environment = var.environment
    }
  )
}

resource "aws_kms_alias" "main" {

  name = "alias/${var.app_name}-${var.environment}-key"

  target_key_id = aws_kms_key.main.key_id
}

############################################################
# CLOUDTRAIL AUDIT LOG STORAGE
############################################################

resource "aws_s3_bucket" "cloudtrail" {

  bucket = "${var.app_name}-${var.environment}-cloudtrail-logs"

  force_destroy = var.environment == "dev" ? true : false

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cloudtrail"
      Environment = var.environment
    }
  )
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {

  bucket = aws_s3_bucket.cloudtrail.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {

  bucket = aws_s3_bucket.cloudtrail.id

  rule {

    apply_server_side_encryption_by_default {

      kms_master_key_id = aws_kms_key.main.arn

      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "cloudtrail" {

  bucket = aws_s3_bucket.cloudtrail.id

  versioning_configuration {

    status = "Enabled"

  }
}

resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail" {

  bucket = aws_s3_bucket.cloudtrail.id

  rule {

    id = "audit-log-retention"

    status = "Enabled"

    expiration {

      days = 365

    }

    abort_incomplete_multipart_upload {

      days_after_initiation = 7

    }
  }
}

############################################################
# CLOUDTRAIL S3 POLICY
############################################################

resource "aws_s3_bucket_policy" "cloudtrail" {

  bucket = aws_s3_bucket.cloudtrail.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AWSCloudTrailAclCheck"

        Effect = "Allow"

        Principal = {

          Service = "cloudtrail.amazonaws.com"

        }

        Action = "s3:GetBucketAcl"

        Resource = aws_s3_bucket.cloudtrail.arn

      },

      {

        Sid = "AWSCloudTrailWrite"

        Effect = "Allow"

        Principal = {

          Service = "cloudtrail.amazonaws.com"

        }

        Action = "s3:PutObject"

        Resource = "${aws_s3_bucket.cloudtrail.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"

        Condition = {

          StringEquals = {

            "s3:x-amz-acl" = "bucket-owner-full-control"

          }

        }

      }

    ]

  })
}

############################################################
# SNS TOPIC FOR CLOUDTRAIL EVENTS
############################################################

resource "aws_sns_topic" "cloudtrail" {

  name = "${var.app_name}-${var.environment}-cloudtrail-topic"

  kms_master_key_id = aws_kms_key.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-cloudtrail-topic"
    }
  )
}

resource "aws_sns_topic_policy" "cloudtrail" {

  arn = aws_sns_topic.cloudtrail.arn

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AllowCloudTrailPublish"

        Effect = "Allow"

        Principal = {

          Service = "cloudtrail.amazonaws.com"

        }

        Action = "sns:Publish"

        Resource = aws_sns_topic.cloudtrail.arn

      }

    ]

  })
}

############################################################
# AWS CLOUDTRAIL
############################################################

resource "aws_cloudtrail" "main" {

  name = "${var.app_name}-${var.environment}-audit-trail"

  s3_bucket_name = aws_s3_bucket.cloudtrail.id

  sns_topic_name = aws_sns_topic.cloudtrail.name

  include_global_service_events = true

  is_multi_region_trail = true

  enable_log_file_validation = true

  kms_key_id = aws_kms_key.main.arn

  depends_on = [

    aws_s3_bucket_policy.cloudtrail,

    aws_sns_topic_policy.cloudtrail

  ]

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-cloudtrail"
    }
  )
}

############################################################
# GUARDDUTY
############################################################

resource "aws_guardduty_detector" "main" {

  enable = true

  finding_publishing_frequency = "FIFTEEN_MINUTES"

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-guardduty"
    }
  )
}

############################################################
# SECURITY HUB
############################################################

resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {

  depends_on = [

    aws_securityhub_account.main

  ]

  standards_arn = "arn:aws:securityhub:${data.aws_region.current.region}::standards/cis-aws-foundations-benchmark/v/3.0.0"

}

############################################################
# AWS CONFIG - COMPLIANCE RECORDING
############################################################

resource "aws_iam_role" "config" {

  name = "${var.app_name}-${var.environment}-config-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "config.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "config" {

  role = aws_iam_role.config.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

resource "aws_s3_bucket" "config" {

  bucket = "${var.app_name}-${var.environment}-config-logs"

  force_destroy = var.environment == "dev" ? true : false

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-config"
    }
  )
}

resource "aws_s3_bucket_versioning" "config" {
  bucket = aws_s3_bucket.config.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "config" {
  bucket = aws_s3_bucket.config.id

  rule {
    id     = "expire-config-logs"
    status = "Enabled"

    expiration {
      days = 365
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "config" {

  bucket = aws_s3_bucket.config.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config" {

  bucket = aws_s3_bucket.config.id

  rule {

    apply_server_side_encryption_by_default {

      kms_master_key_id = aws_kms_key.main.arn

      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_policy" "config" {

  bucket = aws_s3_bucket.config.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "AllowAWSConfigBucketCheck"

        Effect = "Allow"

        Principal = {

          Service = "config.amazonaws.com"

        }

        Action = [

          "s3:GetBucketAcl"

        ]

        Resource = aws_s3_bucket.config.arn

      },

      {

        Sid = "AllowAWSConfigWrite"

        Effect = "Allow"

        Principal = {

          Service = "config.amazonaws.com"

        }

        Action = [

          "s3:PutObject"

        ]

        Resource = "${aws_s3_bucket.config.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/Config/*"

        Condition = {

          StringEquals = {

            "s3:x-amz-acl" = "bucket-owner-full-control"

          }

        }

      }

    ]

  })
}

resource "aws_config_configuration_recorder" "main" {

  name = "${var.app_name}-${var.environment}-config-recorder"

  role_arn = aws_iam_role.config.arn

  recording_group {

    all_supported = true

    include_global_resource_types = true

  }

}

resource "aws_config_delivery_channel" "main" {

  name = "${var.app_name}-${var.environment}-config-channel"

  s3_bucket_name = aws_s3_bucket.config.bucket

  depends_on = [

    aws_s3_bucket_policy.config

  ]
}

resource "aws_config_configuration_recorder_status" "main" {

  name = aws_config_configuration_recorder.main.name

  is_enabled = true

  depends_on = [

    aws_config_delivery_channel.main

  ]
}

############################################################
# CLOUDWATCH LOG GROUP FOR SECURITY EVENTS
############################################################

resource "aws_cloudwatch_log_group" "security" {

  name = "/aws/security/${var.app_name}-${var.environment}"

  retention_in_days = 365

  kms_key_id = aws_kms_key.main.arn

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-security-logs"
    }
  )
}

############################################################
# VPC FLOW LOGS
############################################################

resource "aws_iam_role" "flow_logs" {

  name = "${var.app_name}-${var.environment}-vpc-flowlogs-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "vpc-flow-logs.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]

  })

  tags = var.tags
}

resource "aws_iam_role_policy" "flow_logs" {

  name = "${var.app_name}-${var.environment}-flowlogs-policy"

  role = aws_iam_role.flow_logs.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Action = [

          "logs:CreateLogGroup",

          "logs:CreateLogStream",

          "logs:PutLogEvents",

          "logs:DescribeLogGroups",

          "logs:DescribeLogStreams"

        ]

        Resource = "${aws_cloudwatch_log_group.security.arn}:*"

      }

    ]

  })
}

resource "aws_flow_log" "main" {

  count = var.enable_vpc_flow_logs ? 1 : 0

  iam_role_arn = aws_iam_role.flow_logs.arn

  log_destination = aws_cloudwatch_log_group.security.arn

  traffic_type = "ALL"

  vpc_id = var.vpc_id

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-vpc-flowlogs"
    }
  )
}

############################################################
# CLOUDWATCH LOG RESOURCE POLICY
############################################################

resource "aws_cloudwatch_log_resource_policy" "security" {

  policy_name = "${var.app_name}-${var.environment}-security-log-policy"

  policy_document = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = [

            "vpc-flow-logs.amazonaws.com",

            "config.amazonaws.com"

          ]

        }

        Action = [

          "logs:CreateLogStream",

          "logs:PutLogEvents"

        ]

        Resource = "${aws_cloudwatch_log_group.security.arn}:*"

      }

    ]

  })
}

############################################################
# ECS EXECUTION ROLE
#
# Used by ECS/Fargate agent:
# - Pull images from ECR
# - Write container logs
# - Retrieve secrets during startup
############################################################

resource "aws_iam_role" "ecs_execution_role" {

  name = "${var.app_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "ecs-tasks.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]

  })

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-ecs-execution-role"
    }
  )
}

############################################################
# AWS MANAGED ECS EXECUTION POLICY
############################################################

resource "aws_iam_role_policy_attachment" "ecs_execution" {

  role = aws_iam_role.ecs_execution_role.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"

}

############################################################
# ECS EXECUTION SECRET ACCESS POLICY
############################################################

resource "aws_iam_policy" "ecs_execution_secrets" {

  name = "${var.app_name}-${var.environment}-ecs-secret-access"

  description = "Allow ECS tasks to retrieve encrypted application secrets"

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "SecretsManagerRead"

        Effect = "Allow"

        Action = [

          "secretsmanager:GetSecretValue"

        ]

        Resource = [

          "arn:aws:secretsmanager:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:secret:${var.app_name}/*"

        ]

      },

      {

        Sid = "KMSDecrypt"

        Effect = "Allow"

        Action = [

          "kms:Decrypt",

          "kms:DescribeKey"

        ]

        Resource = aws_kms_key.main.arn

      }

    ]

  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_secrets" {

  role = aws_iam_role.ecs_execution_role.name

  policy_arn = aws_iam_policy.ecs_execution_secrets.arn

}

############################################################
# ECS APPLICATION TASK ROLE
#
# Used by FastAPI / Typesense containers
#
# Allows:
# - Read secrets
# - Read SSM parameters
# - KMS decrypt
############################################################

resource "aws_iam_role" "ecs_task_role" {

  name = "${var.app_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "ecs-tasks.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]

  })

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-ecs-task-role"
    }
  )
}

############################################################
# ECS APPLICATION ACCESS POLICY
############################################################

resource "aws_iam_policy" "ecs_task_application" {

  name = "${var.app_name}-${var.environment}-ecs-task-policy"

  description = "Application permissions for ECS workloads"

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Sid = "ReadSecrets"

        Effect = "Allow"

        Action = [

          "secretsmanager:GetSecretValue"

        ]

        Resource = [

          "arn:aws:secretsmanager:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:secret:${var.app_name}/*"

        ]

      },

      {

        Sid = "ReadParameters"

        Effect = "Allow"

        Action = [

          "ssm:GetParameter",

          "ssm:GetParameters"

        ]

        Resource = [

          "arn:aws:ssm:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:parameter/${var.app_name}/*"

        ]

      },

      {

        Sid = "DecryptApplicationSecrets"

        Effect = "Allow"

        Action = [

          "kms:Decrypt",

          "kms:GenerateDataKey",

          "kms:DescribeKey"

        ]

        Resource = aws_kms_key.main.arn

      }

    ]

  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_application" {

  role = aws_iam_role.ecs_task_role.name

  policy_arn = aws_iam_policy.ecs_task_application.arn

}

############################################################
# ECS TASK ROLE - CLOUDWATCH METRICS
############################################################

resource "aws_iam_policy" "ecs_cloudwatch_metrics" {

  name = "${var.app_name}-${var.environment}-ecs-cloudwatch-policy"

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Action = [

          "cloudwatch:PutMetricData"

        ]

        Resource = "*"

      }

    ]

  })
}

resource "aws_iam_role_policy_attachment" "ecs_cloudwatch_metrics" {

  role = aws_iam_role.ecs_task_role.name

  policy_arn = aws_iam_policy.ecs_cloudwatch_metrics.arn

}

############################################################
# SECURITY GROUP: APPLICATION LOAD BALANCER
#
# Internet facing ALB:
# - Accept HTTPS traffic
# - Redirect HTTP -> HTTPS
# - Forward traffic to FastAPI ECS service
############################################################

resource "aws_security_group" "alb" {

  name = "${var.app_name}-${var.environment}-alb-sg"

  description = "Security group for Application Load Balancer"

  vpc_id = var.vpc_id

  ingress {

    description = "HTTPS from Internet"

    from_port = 443

    to_port = 443

    protocol = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]

  }

  ingress {

    description = "HTTP redirect"

    from_port = 80

    to_port = 80

    protocol = "tcp"

    cidr_blocks = [
      "0.0.0.0/0"
    ]

  }

  egress {

    description = "Allow outbound traffic"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-alb-sg"
    }
  )
}

############################################################
# SECURITY GROUP: FASTAPI ECS SERVICE
#
# Allows:
# ALB -> FastAPI :8000
# FastAPI -> internal services
############################################################

resource "aws_security_group" "fastapi" {

  name = "${var.app_name}-${var.environment}-fastapi-sg"

  description = "FastAPI ECS task security group"

  vpc_id = var.vpc_id

  ingress {

    description = "Traffic from ALB"

    from_port = 8000

    to_port = 8000

    protocol = "tcp"

    security_groups = [
      aws_security_group.alb.id
    ]

  }

  egress {

    description = "Outbound inside VPC"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      var.vpc_cidr
    ]

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-fastapi-sg"
    }
  )
}

############################################################
# SECURITY GROUP: TYPESENSE SEARCH SERVICE
#
# Private ECS service
#
# Only FastAPI can communicate with Typesense
############################################################

resource "aws_security_group" "typesense" {

  name = "${var.app_name}-${var.environment}-typesense-sg"

  description = "Typesense ECS service security group"

  vpc_id = var.vpc_id

  ingress {

    description = "FastAPI access to Typesense"

    from_port = 8108

    to_port = 8108

    protocol = "tcp"

    security_groups = [
      aws_security_group.fastapi.id
    ]

  }

  egress {

    description = "Allow internal communication"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      var.vpc_cidr
    ]

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-typesense-sg"
    }
  )

}

############################################################
# SECURITY GROUP: EFS
#
# Typesense persistent storage
#
# Allows NFS only from Typesense ECS tasks
############################################################

resource "aws_security_group" "efs" {

  name = "${var.app_name}-${var.environment}-efs-sg"

  description = "EFS mount target security group"

  vpc_id = var.vpc_id

  ingress {

    description = "NFS from Typesense"

    from_port = 2049

    to_port = 2049

    protocol = "tcp"

    security_groups = [
      aws_security_group.typesense.id
    ]

  }

  egress {

    description = "Allow VPC communication"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      var.vpc_cidr
    ]

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-efs-sg"
    }
  )

}

############################################################
# SECURITY GROUP: RDS POSTGRESQL
#
# Private database
#
# Only FastAPI can connect
############################################################

resource "aws_security_group" "rds" {

  name = "${var.app_name}-${var.environment}-rds-sg"

  description = "PostgreSQL RDS security group"

  vpc_id = var.vpc_id

  ingress {

    description = "PostgreSQL from FastAPI"

    from_port = 5432

    to_port = 5432

    protocol = "tcp"

    security_groups = [
      aws_security_group.fastapi.id
    ]

  }

  egress {

    description = "Allow internal responses"

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [
      var.vpc_cidr
    ]

  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-rds-sg"
    }
  )

}
