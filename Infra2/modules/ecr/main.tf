# Create an ECR repository for the frontend application
resource "aws_ecr_repository" "frontend" {
  name                 = "frontend-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name = "frontend-repo"
  }
}

# Create an ECR repository for the api-gateway application
resource "aws_ecr_repository" "api-gateway" {
  name                 = "api-gateway-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name = "api-gateway-repo"
  }
}

# Create an ECR repository for the runner application
resource "aws_ecr_repository" "runner" {
  name                 = "runner-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name = "runner-repo"
  }
}

# Create an ECR repository for the geolocation application
resource "aws_ecr_repository" "geolocation" {
  name                 = "geolocation-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name = "geolocation-repo"
  }
}