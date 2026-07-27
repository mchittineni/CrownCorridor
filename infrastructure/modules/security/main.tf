# AWS KMS Customer Managed Key (CMK)
resource "aws_kms_key" "main" {
  description             = "${var.app_name}-${var.environment} encryption key for RDS, S3, SecretsManager, CloudWatch"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-kms-key"
      Environment = var.environment
    }
  )
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.app_name}-${var.environment}-key"
  target_key_id = aws_kms_key.main.key_id
}

# CloudTrail Audit Log Bucket
resource "aws_s3_bucket" "cloudtrail" {
  bucket        = "${var.app_name}-${var.environment}-cloudtrail-logs"
  force_destroy = var.environment == "dev" ? true : false

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cloudtrail-logs"
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
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail.arn}/AWSLogs//*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# AWS CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "${var.app_name}-${var.environment}-audit-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.main.arn

  depends_on = [aws_s3_bucket_policy.cloudtrail]

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-cloudtrail"
      Environment = var.environment
    }
  )
}

# AWS GuardDuty Threat Detection
resource "aws_guardduty_detector" "main" {
  enable = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-guardduty"
      Environment = var.environment
    }
  )
}

# AWS Security Hub Posture Monitoring
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.4.0"
}

# IAM Roles for ECS Execution & Task
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.app_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

# Policy allowing ECS task to decrypt with KMS & access SecretsManager
resource "aws_iam_policy" "ecs_task_kms_secrets" {
  name        = "${var.app_name}-${var.environment}-task-kms-policy"
  description = "Policy for KMS decryption and SecretsManager access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.main.arn
      },
      {
        Effect = "Allow"
        Action = ["secretsmanager:GetSecretValue", "ssm:GetParameters", "ssm:GetParameter"]
        Resource = [
          "arn:aws:secretsmanager:*:*:secret:${var.app_name}/*",
          "arn:aws:ssm:*:*:parameter/${var.app_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_kms" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_kms_secrets.arn
}

# --- SECURITY GROUPS ---

# 1. API Gateway / ALB Security Group
resource "aws_security_group" "api_gateway" {
  name        = "${var.app_name}-${var.environment}-apigw-sg"
  description = "Security group for API Gateway / Entry Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTP from internet (redirects to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all egress"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-apigw-sg"
      Environment = var.environment
    }
  )
}

# 2. FastAPI Container Security Group
resource "aws_security_group" "fastapi" {
  name        = "${var.app_name}-${var.environment}-fastapi-sg"
  description = "Security group for FastAPI microservice"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow port 8000 from API Gateway SG"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.api_gateway.id]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-fastapi-sg"
      Environment = var.environment
    }
  )
}

# 3. Typesense Search Container Security Group
resource "aws_security_group" "typesense" {
  name        = "${var.app_name}-${var.environment}-typesense-sg"
  description = "Security group for Typesense search service"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow Typesense port 8108 from FastAPI SG"
    from_port       = 8108
    to_port         = 8108
    protocol        = "tcp"
    security_groups = [aws_security_group.fastapi.id]
  }

  egress {
    description = "Allow outbound to private VPC services"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-typesense-sg"
      Environment = var.environment
    }
  )
}

# 4. EFS Storage Security Group (for Typesense volume)
resource "aws_security_group" "efs" {
  name        = "${var.app_name}-${var.environment}-efs-sg"
  description = "Security group for EFS persistent storage"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow NFS port 2049 from Typesense SG"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.typesense.id]
  }

  egress {
    description = "Allow outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-efs-sg"
      Environment = var.environment
    }
  )
}

# 5. RDS PostGIS Database Security Group
resource "aws_security_group" "rds" {
  name        = "${var.app_name}-${var.environment}-rds-sg"
  description = "Security group for RDS PostGIS database in private subnet"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow PostgreSQL port 5432 from FastAPI SG"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.fastapi.id]
  }

  egress {
    description = "No outbound required for database"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-rds-sg"
      Environment = var.environment
    }
  )
}
