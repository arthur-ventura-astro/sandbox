locals {
  repository_name = "${module.data.project_name}-airflow"
  access_type = "direct"

  role_access = local.access_type == "role" ? 1 : 0
  direct_access = local.access_type == "direct" ? 1 : 0
}

module "ecr_role" {
  count = local.role_access
  source = "terraform-aws-modules/ecr/aws"

  repository_name = local.repository_name
  repository_read_access_arns = [
    aws_iam_role.ecr_access.arn
  ]
  repository_lifecycle_policy = jsonencode(local.lifecycle_policy)
}

module "ecr_direct" {
  count = local.direct_access
  source = "terraform-aws-modules/ecr/aws"

  repository_name = local.repository_name
  create_registry_policy = true
  registry_policy        = jsonencode(local.registry_policy)
  repository_lifecycle_policy = jsonencode(local.lifecycle_policy)
}
