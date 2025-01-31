variable "aws_access_key_id" {
  type = string
  sensitive = true
}
variable "aws_secret_access_key" {
  type = string
  sensitive = true
}

resource "aws_ssm_parameter" "airflow_aws_default" {
    name = "/airflow/connections/aws_default"
    type = "SecureString"
    value = "aws://${var.aws_access_key_id}:${var.aws_secret_access_key}@/?region_name=us-east-2&role_arn=${aws_iam_role.deployments.arn}"
}
