module "data" {
  source = "./data"
}

terraform {
  required_version = ">=1.4"
  backend "local" {
    path = "./.states/terraform.tfstate"
  }
}

provider "aws" {
  profile = "training"
  region  = module.data.project_region
}

resource "aws_s3_bucket" "states_bucket" {
  bucket = module.data.project_bucket
}