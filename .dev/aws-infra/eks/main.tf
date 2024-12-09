module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = module.data.eks_name
  cluster_version = "1.31"

  # Optional
  cluster_endpoint_public_access = false
  # Optional: Adds the current caller identity as an administrator via cluster access entry
  enable_cluster_creator_admin_permissions = true

  vpc_id     = local.vpc_id
  subnet_ids = local.vpc_private_subnets


  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    instance_types = ["t3.small", "t3.medium"]
  }
  eks_managed_node_groups = {
    general = {
      min_size     = 1
      max_size     = 2
      desired_size = 1
    }
  }

  access_entries = {
    deployments = {
      principal_arn = aws_iam_role.deployment_access.arn

      policy_associations = {
        deployments = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"
          access_scope = {
            namespaces = ["default"]
            type       = "namespace"
          }
        }
      }
    }
  }

  depends_on = [
    aws_iam_role.deployment_access
  ]
}