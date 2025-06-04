module "aws_data" {
  source = "../../aws-infra/data"
}

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
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
  }
}

provider "local" {}
provider "astro" {
  organization_id = var.organization
  token = var.workspace_token
}
provider "github" {
  token = var.github_token
}
provider "aws" {
  profile = "training"
  region  = module.aws_data.project_region
  default_tags {
    tags = module.aws_data.project_tags
  }
}