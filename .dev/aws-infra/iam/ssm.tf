resource "aws_ssm_parameter" "role_arn" {
  name = "${module.data.project_ssm}/iam/deployments-role-arn"
  type = "String"
  value = aws_iam_role.deployments.arn
}

data "aws_ssm_parameter" "experimental_identity" {
  name = "${module.data.project_ssm}/astro/experimental/workload-identity"
}
