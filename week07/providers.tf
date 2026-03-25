# providers.tf

terraform {
  backend "s3" {
    bucket  = "km-state-bucket-devops"
    key     = "jan26/week6/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      repo      = "jan26-bootcamp"
      terraform = "true"
    }
  }
}