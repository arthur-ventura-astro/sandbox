resource "aws_ssm_parameter" "vpc_id" {
  name = "${module.data.project_ssm}/vpc/id"
  type = "String"
  value = module.vpc.vpc_id
}

resource "aws_ssm_parameter" "vpc_private_subnets" {
  name = "${module.data.project_ssm}/vpc/private-subnets"
  type = "String"
  value = join(",", module.vpc.private_subnets)
}

resource "aws_ssm_parameter" "vpc_public_subnets" {
  name = "${module.data.project_ssm}/vpc/public-subnets"
  type = "String"
  value = join(",", module.vpc.public_subnets)
}

resource "aws_ssm_parameter" "vpc_sg" {
    name = "${module.data.project_ssm}/vpc/security-group"
    type = "String"
    value = module.security_group.security_group_id
}