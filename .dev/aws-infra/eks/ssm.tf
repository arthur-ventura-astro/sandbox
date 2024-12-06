locals {
    vpc_id = data.aws_ssm_parameter.vpc_id.value
    vpc_private_subnets = split(",", data.aws_ssm_parameter.vpc_private_subnets.value)
}

data "aws_ssm_parameter" "vpc_id" {
  name = "${module.data.project_ssm}/vpc/id"
}
data "aws_ssm_parameter" "vpc_private_subnets" {
  name = "${module.data.project_ssm}/vpc/private-subnets"
}