# AWS Infra

Infrastructure Order:
0. Terraform
0.0 Base / `aws-infra/`

1. Essentials
1.1 VPC / `aws-infra/vpc`
1.2 IAM / `aws-infra/iam`
1.3 DNS / `aws-infra/dns`

2. Services
2.1 S3 / `aws-infra/s3`
2.2 BH (VPC) / `aws-infra/bastion-host`
2.3 EKS (VPC, IAM) / `aws-infra/eks`
2.4 ECR (VPC, IAM) / `aws-infra/ecr`
2.5 VPN (VPC, DNS) / `aws-infra/vpn`
2.6 RDS (VPC, IAM) / `aws-infra/rds`
