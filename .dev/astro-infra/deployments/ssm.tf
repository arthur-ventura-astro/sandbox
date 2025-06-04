resource "aws_ssm_parameter" "experimental_identity" {
  name = "${module.aws_data.project_ssm}/astro/experimental/workload-identity"
  type = "String"
  value = astro_deployment.experimental.workload_identity
}
