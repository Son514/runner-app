# Define the AWS region
variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-southeast-1"
}

# Define the VPC CIDR block
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Define the Public Subnet CIDR block
variable "public_subnet_cidr" {
  description = "CIDR block for the Public Subnet"
  type        = string
  default     = "10.0.1.0/24"
}

# Define the Private Subnet CIDR block
variable "private_subnet_cidr" {
  description = "CIDR block for the Private Subnet"
  type        = string
  default     = "10.0.2.0/24"
}