locals {
  namespace = "general"
}

resource "kubernetes_namespace" "general" {
  metadata {
    name = local.namespace
  }
}
