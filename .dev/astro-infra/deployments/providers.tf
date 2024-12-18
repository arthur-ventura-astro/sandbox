terraform {
  required_version = ">=1.4"
  backend "s3" {
    profile = "training"
    bucket  = "astro-sandbox-terraform"
    key     = "states/astro/deployments/terraform.tfstate"
    encrypt = true
    region  = "us-east-2"
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
