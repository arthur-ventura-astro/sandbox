locals {
  vpc_name = "${local.project_name}-vpc"
  vpc_sg = "${local.vpc_name}-sg"
  vpc_azs = [
    "${local.project_region}a",
    "${local.project_region}b",
    "${local.project_region}c"
  ]
}

output "vpc_name" {
  value = local.vpc_name
}

output "vpc_sg" {
  value = local.vpc_sg
}

output "vpc_azs" {
  value = local.vpc_azs
}
