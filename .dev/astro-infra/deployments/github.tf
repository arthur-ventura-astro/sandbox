resource "github_actions_variable" "experimental_deployment" {
  repository       = local.repository
  variable_name    = "EXP_ASTRO_DEPLOYMENT_ID"
  value            = astro_deployment.experimental.id
}

resource "github_actions_secret" "experimental_token" {
  repository       = local.repository
  secret_name      = "EXP_ASTRO_API_TOKEN"
  plaintext_value  = astro_api_token.experimental.token
}
