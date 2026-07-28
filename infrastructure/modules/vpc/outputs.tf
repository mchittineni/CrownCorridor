#############################################
# VPC Outputs
#############################################

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

#############################################
# Internet Gateway
#############################################

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

#############################################
# Subnet Outputs
#############################################

output "public_subnet_ids" {
  description = "List of public subnet IDs used for ALB and internet-facing resources"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs used for ECS/Fargate workloads"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "List of private database subnet IDs used for RDS"
  value       = aws_subnet.database[*].id
}

output "availability_zones" {
  description = "Availability zones used by the VPC"
  value       = var.availability_zones
}

#############################################
# Routing Outputs
#############################################

output "public_route_table_id" {
  description = "Public route table ID"
  value       = aws_route_table.public.id
}

output "private_route_table_id" {
  description = "Private route table ID"
  value       = aws_route_table.private.id
}

#############################################
# NAT Gateway Outputs
#############################################

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = aws_nat_gateway.main.id
}

output "nat_gateway_public_ip" {
  description = "Elastic IP address assigned to NAT Gateway"
  value       = aws_eip.nat.public_ip
}

#############################################
# RDS Outputs
#############################################

output "db_subnet_group_name" {
  description = "Name of the RDS DB subnet group"
  value       = aws_db_subnet_group.main.name
}

output "db_subnet_group_id" {
  description = "ID of the RDS DB subnet group"
  value       = aws_db_subnet_group.main.id
}

#############################################
# VPC Flow Logs Outputs
#############################################

output "vpc_flow_log_id" {
  description = "ID of the VPC Flow Log resource"
  value       = aws_flow_log.main.id
}

output "vpc_flow_log_group_name" {
  description = "CloudWatch Log Group used for VPC Flow Logs"
  value       = aws_cloudwatch_log_group.flow_logs.name
}
