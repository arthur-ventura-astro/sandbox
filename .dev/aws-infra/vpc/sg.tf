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
  ingress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "Allow all inbound traffic"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_self = [
    {
      rule = "all-all"
    }
  ]
  egress_with_cidr_blocks = [
    {
      rule        = "https-443-tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}
