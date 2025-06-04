locals {
  vpc_id = data.aws_ssm_parameter.vpc_id.value
  vpc_security_group = data.aws_ssm_parameter.vpc_sg.value
  private_subnets = split(",", data.aws_ssm_parameter.private_subnets.value)
  public_subnets = split(",", data.aws_ssm_parameter.public_subnets.value)
  domain = data.aws_ssm_parameter.domain.value
  certificate_arn = data.aws_ssm_parameter.certificate.value
}

data "aws_ssm_parameter" "vpc_id" {
    name = "${module.data.project_ssm}/vpc/id"
}
data "aws_ssm_parameter" "vpc_sg" {
    name = "${module.data.project_ssm}/vpc/security-group"
}
data "aws_ssm_parameter" "private_subnets" {
    name = "${module.data.project_ssm}/vpc/private-subnets"
}
data "aws_ssm_parameter" "public_subnets" {
    name = "${module.data.project_ssm}/vpc/public-subnets"
}

data "aws_ssm_parameter" "domain" {
  name = "${module.data.project_ssm}/dns/domain"
}
data "aws_ssm_parameter" "certificate" {
  name = "${module.data.project_ssm}/dns/certificate"
}
