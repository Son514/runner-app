output "frontend_repository_url" {
  description = "URL of the frontend ECR repository"
  value       = aws_ecr_repository.frontend.repository_url
}

output "api_gateway_repository_url" {
  description = "URL of the API Gateway ECR repository"
  value       = aws_ecr_repository.api-gateway.repository_url
}

output "runner_repository_url" {
  description = "URL of the Runner ECR repository"
  value       = aws_ecr_repository.runner.repository_url
}

output "geolocation_repository_url" {
  description = "URL of the Geolocation ECR repository"
  value       = aws_ecr_repository.geolocation.repository_url
}