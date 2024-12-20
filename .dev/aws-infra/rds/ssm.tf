locals {
  vpc_id = data.aws_ssm_parameter.vpc_id.value
  vpc_security_group = data.aws_ssm_parameter.vpc_sg.value
  public_subnets = split(",", data.aws_ssm_parameter.public_subnets.value)
}

data "aws_ssm_parameter" "vpc_id" {
    name = "${module.data.project_ssm}/vpc/id"
}
data "aws_ssm_parameter" "vpc_sg" {
    name = "${module.data.project_ssm}/vpc/security-group"
}
data "aws_ssm_parameter" "public_subnets" {
    name = "${module.data.project_ssm}/vpc/public-subnets"
}
