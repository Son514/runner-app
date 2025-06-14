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

output "frontend_repository_url" {
  description = "URL of the Frontend ECR repository"
  value       = module.ecr.frontend_repository_url
}

output "api_gateway_repository_url" {
  description = "URL of the API Gateway ECR repository"
  value       = module.ecr.api_gateway_repository_url
}

output "runner_repository_url" {
  description = "URL of the Runner ECR repository"
  value       = module.ecr.runner_repository_url
}

output "geolocation_repository_url" {
  description = "URL of the Geolocation ECR repository"
  value       = module.ecr.geolocation_repository_url
}