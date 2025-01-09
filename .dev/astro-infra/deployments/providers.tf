terraform {
  required_version = ">=1.4"
  backend "local" {
    path = "../.states/terraform.tfstate"
  }

  required_providers {
    astro = {
      source  = "astronomer/astro"
      version = "1.0.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "astro" {
  organization_id = var.organization
  token = var.workspace_token
}
provider "github" {
  token = var.github_token
}
