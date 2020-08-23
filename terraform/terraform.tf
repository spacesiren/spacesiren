# Backend and AWS provider settings are in terraform-local.tf.example.
# Copy that file to terraform-local.tf.

terraform {
  required_version = ">= 0.13"

  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 1.3.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 2.3.0"
    }
  }
}
