locals {
  eks_name = "${local.project_name}-cluster"
}

output "eks_name" {
  value = local.eks_name
}
