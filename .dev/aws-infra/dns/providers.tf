module "data" {
  source = "../data"
}

terraform {
  required_version = ">=1.4"
  backend "s3" {
    profile = "training"
    bucket  = "astro-sandbox-terraform"
    key     = "states/dns/terraform.tfstate"
    encrypt = true
    region  = "us-east-2"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
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

provider "aws" {
  alias   = "owner"
  profile = local.owner_profile
  region  = local.owner_region
  default_tags {
    tags = module.data.project_tags
  }
}