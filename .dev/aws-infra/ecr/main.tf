locals {
  repository_name = "${module.data.project_name}-custom"
}

module "ecr" {
  source = "terraform-aws-modules/ecr/aws"

  repository_force_delete = true
  repository_image_tag_mutability = "MUTABLE"

  repository_name = local.repository_name
  repository_read_access_arns = [
    local.deployments_role
  ]
  repository_lifecycle_policy = jsonencode({
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
  })
}
