resource "aws_ssm_parameter" "domain" {
  name = "${module.data.project_ssm}/dns/domain"
  type = "String"
  value = local.full_domain
}

resource "aws_ssm_parameter" "certificate" {
  name = "${module.data.project_ssm}/dns/certificate"
  type = "String"
  value = module.acm.acm_certificate_arn
}
