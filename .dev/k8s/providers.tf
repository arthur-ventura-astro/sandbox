terraform {
  backend "local" {
    path = "./.states/k8s.tfstate"
  }

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.11.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/sandbox_config"
}
