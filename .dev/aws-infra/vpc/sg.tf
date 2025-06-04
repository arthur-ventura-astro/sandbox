variable "ipv4_allow_list" {
  type    = string
  default = ""
}
variable "ipv6_allow_list" {
  type    = string
  default = ""
}
locals {
  ipv4_allow_list = var.ipv4_allow_list != "" ? split(",", var.ipv4_allow_list) : []
  ipv6_allow_list = var.ipv6_allow_list != "" ? split(",", var.ipv6_allow_list) : []
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "4.17.1"

  name   = module.data.vpc_sg
  vpc_id = module.vpc.vpc_id

  ingress_with_self = [
    {
      rule = "all-all"
    }
  ]
  egress_with_self = [
    {
      rule = "all-all"
    }
  ]
  egress_with_cidr_blocks = [
    {
      rule             = "https-443-tcp"
      cidr_blocks      = "0.0.0.0/0"
      cidr_ipv6 = "::/0"
    }
  ]
}

resource "aws_security_group_rule" "tcp_ingress" {
  for_each = toset(module.data.tcp_access)
  
  type = "ingress"
  from_port   = tonumber(each.key)
  to_port     = tonumber(each.key)
  protocol    = "tcp"
  cidr_blocks = local.ipv4_allow_list
  ipv6_cidr_blocks = local.ipv6_allow_list
  security_group_id = module.security_group.security_group_id
}

resource "aws_security_group_rule" "udp_ingress" {
  for_each = toset(module.data.udp_access)
  
  type = "ingress"
  from_port   = tonumber(each.key)
  to_port     = tonumber(each.key)
  protocol    = "udp"
  cidr_blocks = local.ipv4_allow_list
  ipv6_cidr_blocks = local.ipv6_allow_list
  security_group_id = module.security_group.security_group_id
}

resource "aws_security_group_rule" "egress" {
  for_each = toset(module.data.udp_access)
  
  type = "egress"
  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]
  security_group_id = module.security_group.security_group_id
}
