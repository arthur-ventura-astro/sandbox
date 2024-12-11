module "data" {
  source = "../data"
}

terraform {
  required_version = ">=1.4"
  backend "s3" {
    profile = "training"
    bucket  = "astro-sandbox-terraform"
    key     = "states/vpn/terraform.tfstate"
    encrypt = true
    region  = "us-east-2"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
    tls = {
      source  = "hashicorp/tls"
      version = ">= 4.0.4"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.4.0"
    }
  }
}

provider "aws" {
  profile = "training"
  region  = module.data.project_region
  default_tags {
    tags = module.data.project_tags
  }
}