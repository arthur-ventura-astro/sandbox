locals {
  data_bucket = "${local.project_name}-data"
  xcom_bucket = "${local.project_name}-xcom"
}

output "data_bucket" {
  value = local.data_bucket
}
output "xcom_bucket" {
  value = local.xcom_bucket
}