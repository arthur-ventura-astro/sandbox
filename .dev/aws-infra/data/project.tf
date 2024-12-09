locals {
  project_name   = "astro-sandbox"
  project_region = "us-east-2"
  project_ssm = "/${local.project_name}"
  project_bucket = "${local.project_name}-terraform"
  
  project_tags = {
    Project = "Astro"
  }
}

output "project_name" {
  value = local.project_name
}

output "project_region" {
  value = local.project_region
}

output "project_ssm" {
  value = local.project_ssm
}

output "project_bucket" {
  value = local.project_bucket
}

output "project_tags" {
  value = local.project_tags
}
