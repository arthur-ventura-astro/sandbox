resource "aws_ssm_parameter" "role_arn" {
  name = "${module.data.project_ssm}/iam/deployments-role-arn"
  type = "String"
  value = aws_iam_role.deployments.arn
}
