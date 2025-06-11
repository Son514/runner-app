# Output the VPC ID
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

# Output the Public Subnet ID
output "public_subnet_id" {
  description = "ID of the Public Subnet"
  value       = aws_subnet.public.id
}

# Output the Private Subnet ID
output "private_subnet_id" {
  description = "ID of the Private Subnet"
  value       = aws_subnet.private.id
}