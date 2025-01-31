resource "astro_deployment" "experimental" {
  original_astro_runtime_version = "12.4.0"
  name                           = "sandbox-experimental"
  description                    = "Experimental deployment for sandbox project."

  type       = "DEDICATED"
  cluster_id = var.cluster

  contact_emails = [var.contact]

  default_task_pod_cpu    = "0.25"
  default_task_pod_memory = "0.5Gi"

  executor = "CELERY"
  worker_queues = [{
    name               = "default"
    is_default         = true
    astro_machine      = "A5"
    max_worker_count   = 10
    min_worker_count   = 0
    worker_concurrency = 1
  }]

  is_cicd_enforced      = true
  is_dag_deploy_enabled = true
  is_development_mode   = false
  is_high_availability  = true

  resource_quota_cpu    = "10"
  resource_quota_memory = "20Gi"
  scheduler_size        = "SMALL"
  workspace_id          = var.workspace

  environment_variables = [{
      key       = "AWS_ACCESS_KEY_ID"
      value     = var.aws_access_key_id
      is_secret = true
    }, {
      key       = "AWS_SECRET_ACCESS_KEY"
      value     = var.aws_secret_access_key
      is_secret = true
    },
    {
      key       = "AWS_DEFAULT_REGION"
      value     = "us-east-2"
      is_secret = false
    },
    {
      key       = "AIRFLOW__SECRETS__BACKEND"
      value     = "airflow.providers.amazon.aws.secrets.systems_manager.SystemsManagerParameterStoreBackend"
      is_secret = false
    }, {
      key       = "AIRFLOW__SECRETS__BACKEND_KWARGS"
      value     = "{\"connections_prefix\": \"airflow/connections\", \"variables_prefix\": \"airflow/variables\"}"
      is_secret = false
  }]
}

resource "astro_api_token" "experimental" {
  name = "experimental-token"
  type = "DEPLOYMENT"
  roles = [{
    "role" : "DEPLOYMENT_ADMIN",
    "entity_id" : astro_deployment.experimental.id,
    "entity_type" : "DEPLOYMENT"
  }]
}


