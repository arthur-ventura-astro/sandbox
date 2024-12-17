resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id = local.vpc_id
  service_name = "com.amazonaws.${module.data.project_region}.ecr.dkr"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true
  security_group_ids = [aws_security_group.ecr_endpoint_sg.id]
  subnet_ids = local.vpc_private_subnets
}

resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id = local.vpc_id
  service_name = "com.amazonaws.${module.data.project_region}.ecr.api"
  vpc_endpoint_type = "Interface"
  private_dns_enabled = true
  security_group_ids = [aws_security_group.ecr_endpoint_sg.id]
  subnet_ids = local.vpc_private_subnets
}

resource "aws_security_group" "ecr_endpoint_sg" {
  name        = "${module.data.project_name}-ecr-endpoint-sg"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = local.ipv4_allow_list
    ipv6_cidr_blocks = local.ipv6_allow_list
  }
}