variable "rds_password" {
  default = "postgres"
}
variable "rds_username" {
  default = "postgres"
}

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

resource "aws_ssm_parameter" "rds_endpoint" {
    name = "${module.data.project_ssm}/rds/endpoint"
    type = "String"
    value = module.postgres.db_instance_endpoint
}

resource "aws_ssm_parameter" "rds_user" {
    name = "${module.data.project_ssm}/rds/user"
    type = "String"
    value = var.rds_username
}

resource "aws_ssm_parameter" "rds_pass" {
    name = "${module.data.project_ssm}/rds/password"
    type = "SecureString"
    value = var.rds_password
}