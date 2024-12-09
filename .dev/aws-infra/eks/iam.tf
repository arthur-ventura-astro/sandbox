locals {
    aws_policies = [
        "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
        "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
        "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    ]
}
variable "user_arn" {
  type = string
  sensitive = true
}
variable "dev_deployment_arn" {
  type = string
  sensitive = true
}
variable "prod_deployment_arn" {
  type = string
  sensitive = true
}

resource "aws_iam_role" "deployment_access" {
  name = "${module.data.eks_name}-deployment-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = [
            "${var.user_arn}",
            "${var.dev_deployment_arn}",
            "${var.prod_deployment_arn}"
          ]
          Service = [
            "ec2.amazonaws.com",
            "eks.amazonaws.com"
          ]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "policies_attach" {
  for_each = toset(local.aws_policies)

  role       = aws_iam_role.deployment_access.name
  policy_arn = each.value
}
