# Terraform configuration for AWS architecture with VPC, EKS, and related components

# Specify required providers and versions
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Configure the AWS provider
provider "aws" {
  region = "ap-southeast-1" # Change to your preferred region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "my-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "my-igw"
  }
}

# Route Table for Public Subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = {
    Name = "public-route-table"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "ap-southeast-1a"
  tags = {
    Name = "public-subnet"
  }
}

# Associate Route Table with Public Subnet
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Private Subnet 1
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-southeast-1a"
  tags = {
    Name = "private-subnet-1"
  }
}

# Private Subnet 2
resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "ap-southeast-1b"
  tags = {
    Name = "private-subnet-2"
  }
}

# NAT Gateway (requires an Elastic IP)
resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
  tags = {
    Name = "my-nat-gateway"
  }
}

# Route Table for Private Subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
  tags = {
    Name = "private-route-table"
  }
}

# Associate Route Table with Private Subnets
resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}

# Security Group for EC2 (Jenkins)
resource "aws_security_group" "jenkins" {
  vpc_id = aws_vpc.main.id
  name   = "jenkins-sg"
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "jenkins-sg"
  }
}

# EC2 Instance for Jenkins
# resource "aws_instance" "jenkins" {
#   ami                    = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI (ap-southeast-1, update if needed)
#   instance_type          = "t2.micro"
#   subnet_id              = aws_subnet.public.id
#   vpc_security_group_ids = [aws_security_group.jenkins.id]
#   user_data = <<-EOF
#               #!/bin/bash
#               yum update -y
#               yum install -y java-1.8.0-openjdk
#               wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
#               rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
#               yum install -y jenkins
#               systemctl start jenkins
#               systemctl enable jenkins
#               EOF
#   tags = {
#     Name = "jenkins-server"
#   }
# }

# IAM Role for EKS Cluster
resource "aws_iam_role" "eks_cluster" {
  name = "eks-cluster-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "my-eks-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_group_ids = [aws_security_group.eks_nodes.id]
  }
  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}

# IAM Role for EKS Nodes
resource "aws_iam_role" "eks_nodes" {
  name = "eks-nodes-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_nodes.name
}

resource "aws_iam_role_policy_attachment" "ec2_container_registry" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_nodes.name
}

# Security Group for EKS Nodes
resource "aws_security_group" "eks_nodes" {
  vpc_id = aws_vpc.main.id
  name   = "eks-nodes-sg"
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "eks-nodes-sg"
  }
}

# EKS Node Group (3 nodes)
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "my-eks-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = [aws_subnet.private_1.id, aws_subnet.private_2.id]
  scaling_config {
    desired_size = 3
    max_size     = 3
    min_size     = 3
  }
  instance_types = ["t3.medium"]
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ec2_container_registry
  ]
}

# ECR Repository
# resource "aws_ecr_repository" "frontend" {
#   name = "frontend-app"
# }

# EBS Volume for EKS Persistent Storage
# resource "aws_ebs_volume" "eks_storage" {
#   availability_zone = "ap-southeast-1a"
#   size              = 10 # 10 GiB
#   tags = {
#     Name = "eks-storage"
#   }
# }

# Kubernetes Provider for EKS
provider "kubernetes" {
  host                   = aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      aws_eks_cluster.main.name
    ]
  }
}

# Kubernetes Service for Frontend (creates ELB)
# resource "kubernetes_service" "frontend" {
#   metadata {
#     name = "frontend-service"
#   }
#   spec {
#     selector = {
#       app = "frontend"
#     }
#     port {
#       port        = 80
#       target_port = 8080
#     }
#     type = "LoadBalancer"
#   }
#   depends_on = [aws_eks_node_group.main]
# }

# Output EKS Cluster Endpoint and Jenkins Public IP
# output "eks_cluster_endpoint" {
#   value = aws_eks_cluster.main.endpoint
# }

# output "jenkins_public_ip" {
#   value = aws_instance.jenkins.public_ip
# }

# output "ecr_repository_url" {
#   value = aws_ecr_repository.frontend.repository_url
# }