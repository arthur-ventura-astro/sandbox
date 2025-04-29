module "data" {
  source = "../data"
}

terraform {
  required_version = ">=1.4"
  backend "s3" {
    profile = "training"
    bucket  = "astro-sandbox-terraform"
    key     = "states/grafana/terraform.tfstate"
    encrypt = true
    region  = "us-east-2"
  }

  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.0.0"
    }

    kubernetes = {
      version = ">= 2.0.0"
      source  = "hashicorp/kubernetes"
    }

    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
  }
}


data "aws_eks_cluster" "cluster" {
  name = module.data.eks_name
}
data "aws_eks_cluster_auth" "cluster_auth" {
  name = module.data.eks_name
}


provider "aws" {
  profile = "training"
  region  = module.data.project_region
  default_tags {
    tags = module.data.project_tags
  }
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster_auth.token
  }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster_auth.token
}

provider "kubectl" {
  load_config_file       = false
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster_auth.token
}
