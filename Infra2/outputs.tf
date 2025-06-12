output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_1_id" {
  description = "ID of public subnet 1"
  value       = module.vpc.public_subnet_1_id
}

output "public_subnet_2_id" {
  description = "ID of public subnet 2"
  value       = module.vpc.public_subnet_2_id
}

output "private_subnet_1_id" {
  description = "ID of private subnet 1"
  value       = module.vpc.private_subnet_1_id
}

output "private_subnet_2_id" {
  description = "ID of private subnet 2"
  value       = module.vpc.private_subnet_2_id
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = module.ecr.repository_url
}