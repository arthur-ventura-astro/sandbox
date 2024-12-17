variable "ipv4_allow_list" {
  type = string
  default = "0.0.0.0/0"
}
variable "ipv6_allow_list" {
  type = string
  default = "::/0"
}
locals {
  ipv4_allow_list = split(",", var.ipv4_allow_list)
  ipv6_allow_list = split(",", var.ipv6_allow_list)

  deployments_role    = data.aws_ssm_parameter.deployments_role.value
  vpc_id              = data.aws_ssm_parameter.vpc_id.value
  vpc_private_subnets = split(",", data.aws_ssm_parameter.vpc_private_subnets.value)
}


data "aws_ssm_parameter" "deployments_role" {
  name = "${module.data.project_ssm}/iam/deployments-role-arn"
}
data "aws_ssm_parameter" "vpc_id" {
  name = "${module.data.project_ssm}/vpc/id"
}
data "aws_ssm_parameter" "vpc_private_subnets" {
  name = "${module.data.project_ssm}/vpc/private-subnets"
}