#############################################
# VPC
#############################################

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-vpc"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

#############################################
# Internet Gateway
#############################################

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-igw"
      Environment = var.environment
    }
  )
}

#############################################
# Public Subnets
# ALB / Internet-facing services
#############################################

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-public-${count.index + 1}"
      Environment = var.environment
      Tier        = "Public"
    }
  )
}

#############################################
# Private Application Subnets
# ECS / Fargate / Internal Services
#############################################

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-private-${count.index + 1}"
      Environment = var.environment
      Tier        = "Application"
    }
  )
}

#############################################
# Database Subnets
# RDS PostgreSQL / PostGIS
#############################################

resource "aws_subnet" "database" {
  count = length(var.database_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.database_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-database-${count.index + 1}"
      Environment = var.environment
      Tier        = "Database"
    }
  )
}

#############################################
# NAT Gateway
#############################################

resource "aws_eip" "nat" {

  domain = "vpc"

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-nat-eip"
      Environment = var.environment
    }
  )

}

resource "aws_nat_gateway" "main" {

  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  depends_on = [
    aws_internet_gateway.main
  ]

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-nat"
      Environment = var.environment
    }
  )
}

#############################################
# Public Route Table
#############################################

resource "aws_route_table" "public" {

  vpc_id = aws_vpc.main.id

  route {

    cidr_block = "0.0.0.0/0"

    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-public-rt"
      Environment = var.environment
    }
  )
}

resource "aws_route_table_association" "public" {

  count = length(var.public_subnet_cidrs)

  subnet_id = aws_subnet.public[count.index].id

  route_table_id = aws_route_table.public.id
}

#############################################
# Private Route Table
#############################################

resource "aws_route_table" "private" {

  vpc_id = aws_vpc.main.id

  route {

    cidr_block = "0.0.0.0/0"

    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-private-rt"
      Environment = var.environment
    }
  )
}

resource "aws_route_table_association" "private" {

  count = length(var.private_subnet_cidrs)

  subnet_id = aws_subnet.private[count.index].id

  route_table_id = aws_route_table.private.id
}

#############################################
# Database Route Table Association
#############################################

resource "aws_route_table_association" "database" {

  count = length(var.database_subnet_cidrs)

  subnet_id = aws_subnet.database[count.index].id

  route_table_id = aws_route_table.private.id
}

#############################################
# RDS Subnet Group
#############################################

resource "aws_db_subnet_group" "main" {

  name = "${var.app_name}-${var.environment}-db-subnet-group"

  subnet_ids = aws_subnet.database[*].id

  tags = merge(
    var.tags,
    {
      Name        = "${var.app_name}-${var.environment}-db-subnet-group"
      Environment = var.environment
    }
  )
}

#############################################
# VPC Flow Logs
#############################################

resource "aws_cloudwatch_log_group" "flow_logs" {

  name = "/aws/vpc/${var.app_name}-${var.environment}"

  retention_in_days = 365

  tags = var.tags
}

resource "aws_iam_role" "flow_logs" {

  name = "${var.app_name}-${var.environment}-vpc-flow-role"

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

}

resource "aws_iam_role_policy" "flow_logs" {

  name = "${var.app_name}-${var.environment}-vpc-flow-policy"

  role = aws_iam_role.flow_logs.id

  policy = jsonencode({

    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]

        Resource = "${aws_cloudwatch_log_group.flow_logs.arn}:*"
      }
    ]

  })

}

resource "aws_flow_log" "main" {

  vpc_id = aws_vpc.main.id

  traffic_type = "ALL"

  iam_role_arn = aws_iam_role.flow_logs.arn

  log_destination = aws_cloudwatch_log_group.flow_logs.arn

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-flow-log"
    }
  )

}

#############################################
# Default Security Group Lockdown
#############################################

resource "aws_default_security_group" "default" {

  vpc_id = aws_vpc.main.id

  ingress = []

  egress = []

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-${var.environment}-default-sg-disabled"
    }
  )
}
