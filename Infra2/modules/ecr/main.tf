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