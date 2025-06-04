# docs: https://medium.com/@n.sobadjiev_2847/create-a-vpn-connection-to-your-aws-cluster-terraform-deccbfcbfa1d

resource "aws_acm_certificate" "vpn_server" {
  domain_name = "*.${local.domain}"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_acm_certificate_validation" "vpn_server" {
  certificate_arn = aws_acm_certificate.vpn_server.arn
  timeouts {
    create = "1m"
  }
}

resource "aws_ec2_client_vpn_endpoint" "vpn" {
  description = "VPN endpoint"
  client_cidr_block = "10.1.0.0/16"
  split_tunnel = true
  server_certificate_arn = aws_acm_certificate_validation.vpn_server.certificate_arn
  security_group_ids = [
    aws_security_group.vpn_access.id,
    local.vpc_security_group
  ]

  vpc_id = local.vpc_id
  authentication_options {
    type = "certificate-authentication"
    root_certificate_chain_arn = aws_acm_certificate.ca.arn
  }
  connection_log_options {
    enabled = false
  }

  depends_on = [ aws_acm_certificate.ca ]
}

resource "aws_security_group" "vpn_access" {
  vpc_id = local.vpc_id
  name = "vpn-sg"
  ingress {
    from_port = 0
    protocol = "-1"
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  egress {
    from_port = 0
    protocol = "-1"
    to_port = 0
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}
resource "aws_ec2_client_vpn_network_association" "vpn_subnets" {
  count = length(local.private_subnets)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  subnet_id = element(local.private_subnets, count.index)
  lifecycle {
    // The issue why we are ignoring changes is that on every change
    // terraform screws up most of the vpn assosciations
    // see: https://github.com/hashicorp/terraform-provider-aws/issues/14717
    ignore_changes = [subnet_id]
  }
}

resource "aws_ec2_client_vpn_authorization_rule" "vpn_auth_rule" {
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  target_network_cidr = "10.0.0.0/16"
  authorize_all_groups = true
}