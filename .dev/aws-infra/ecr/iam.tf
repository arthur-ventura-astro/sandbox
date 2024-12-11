variable "user_arn" {
  type = string
}
variable "astro_account" {
  type = string
  default = "-"
}
variable "cluster_id" {
  type = string
  default = "-"
}

locals {
  aws_policy = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"

  lifecycle_policy = {
    rules = [
      {
        rulePriority = 1,
        description  = "Keep last 10 images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["v"],
          countType     = "imageCountMoreThan",
          countNumber   = 10
        },
        action = {
          type = "expire"
        }
      }
    ]
  }

  registry_policy = {
    Version = "2008-10-17",
    Statement = [
      {
        "Sid" : "AllowImagePullAstro",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::${var.astro_account}:role/EKS-NodeInstanceRole-${var.cluster_id}"
        },
        "Action" : [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
      }
    ]
  }
}


resource "aws_iam_role" "ecr_access" {
  name = "${module.data.project_name}-image-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = [
            "${var.user_arn}",
          ]
          Service = [
            "ecr.amazonaws.com"
          ]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "policies_attach" {
  role       = aws_iam_role.ecr_access.name
  policy_arn = local.aws_policy
}
