locals {
  owner_profile="indicium"
  owner_region="us-east-1"
  owner_domain="indicium.tech"
  owner_user="ventura"

  full_domain = "${local.owner_user}-${module.data.project_domain}.${local.owner_domain}"
}


resource "aws_route53_zone" "project_profile" {
  name = local.full_domain
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 4.0"

  domain_name = local.full_domain
  zone_id     = aws_route53_zone.project_profile.zone_id

  subject_alternative_names = [
    "*.${local.full_domain}",
  ]

  wait_for_validation = false

  depends_on = [
    aws_route53_zone.project_profile
  ]
}

data "aws_route53_zone" "main" {
  name = local.owner_domain
  provider = aws.owner
}

resource "aws_route53_record" "main_profile" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = module.data.project_domain
  type    = "NS"
  ttl     = "30"
  records = aws_route53_zone.project_profile.name_servers

  provider = aws.owner
}
