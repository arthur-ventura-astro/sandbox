# Docs: https://chrisguitarguy.com/2023/03/19/create-your-own-certificate-authority-with-terraform/

variable "ca_private_key" {
  type = string
  sensitive = true
}
variable "client_private_key" {
  type = string
  sensitive = true
}


locals {
  ten_years   = 87600
  five_years  = 43830
  ninety_days = 2160

  vpn_dns = "vpn.${local.domain}"
}


## Keys
resource "aws_kms_key" "ca" {
  description = "${module.data.project_name}-vpn-ca"
}

resource "aws_kms_alias" "ca" {
  name          = "alias/${module.data.project_name}-vpn-ca"
  target_key_id = aws_kms_key.ca.key_id
}

resource "aws_ssm_parameter" "ca_private_key" {
  name   = "/${module.data.project_name}/vpn/ca_private_key"
  type   = "SecureString"
  key_id = aws_kms_key.ca.id
  value  = var.ca_private_key
 
  lifecycle {
    ignore_changes = [value]
  }
}
 
resource "aws_ssm_parameter" "client_private_key" {
  name   = "/${module.data.project_name}/vpn/client_private_key"
  type   = "SecureString"
  key_id = aws_kms_key.ca.id
  value  = var.client_private_key
 
  lifecycle {
    ignore_changes = [value]
  }
}


## Root Certificate
resource "tls_self_signed_cert" "ca" {
  private_key_pem   = aws_ssm_parameter.ca_private_key.value
  is_ca_certificate = true
 
  subject {
    common_name         = local.vpn_dns
  }
 
  validity_period_hours = local.ten_years
  early_renewal_hours   = local.ninety_days
 
  allowed_uses = [
    "cert_signing",
    "crl_signing",
    "code_signing",
    "server_auth",
    "client_auth",
    "digital_signature",
    "key_encipherment",
  ]
}

resource "aws_acm_certificate" "ca" {
  private_key      = aws_ssm_parameter.ca_private_key.value
  certificate_body = tls_self_signed_cert.ca.cert_pem
}


## Client Certificate
resource "tls_cert_request" "client" {
  private_key_pem = aws_ssm_parameter.client_private_key.value
 
  subject {
    common_name         = "client.${local.vpn_dns}"
  }
}

resource "tls_locally_signed_cert" "client" {
  cert_request_pem   = tls_cert_request.client.cert_request_pem
  ca_private_key_pem = aws_ssm_parameter.ca_private_key.value
  ca_cert_pem        = tls_self_signed_cert.ca.cert_pem
 
  validity_period_hours = local.five_years
  early_renewal_hours   = local.ninety_days
 
  allowed_uses = [
    "client_auth",
  ]
}

resource "local_file" "client-certificate" {
  content         = tls_locally_signed_cert.client.cert_pem
  filename        = "${path.module}/clients/main.pem"
  file_permission = "0666"
}
