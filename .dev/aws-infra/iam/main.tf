variable "user_arn" {
  type = string
}

locals {
  aws_policies = [
    "arn:aws:iam::aws:policy/ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  ]
}


resource "aws_iam_role" "deployments" {
  name = "${module.data.project_name}-deployments"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = [
            var.user_arn
          ]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "policies_attach" {
  for_each = toset(local.aws_policies)
  role       = aws_iam_role.deployments.name
  policy_arn = each.key
}
