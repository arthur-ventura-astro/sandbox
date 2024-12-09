locals {
  # Define either to connect through SSM or SSH
  use_ssm = false

  # Configure constraints for using SSM/SSH
  ssh_resources = local.use_ssm == true ? 0 : 1
  public_ip = !local.use_ssm
  subnet_id = local.use_ssm == true ? local.private_subnets[0] : local.public_subnets[0]

  # Parsing data from AWS resources
  ami_ssm = aws_ssm_parameter.ami.name
  security_group = data.aws_ssm_parameter.vpc_sg.value
  private_subnets = split(",", data.aws_ssm_parameter.private_subnets.value)
  public_subnets = split(",", data.aws_ssm_parameter.public_subnets.value)
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

data "aws_ami" "default" {
  most_recent = "true"

  dynamic "filter" {
    for_each = {
      name = ["amzn2-ami-hvm-2.*-x86_64-ebs"]
    }
    content {
      name   = filter.key
      values = filter.value
    }
  }

  owners = ["amazon"]

}

resource "aws_ssm_parameter" "ami" {
  name  = "${module.data.project_name}-ami-bastionhost"
  type  = "String"
  value = data.aws_ami.default.id
}