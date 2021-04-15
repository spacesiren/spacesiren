# Backend and AWS provider settings are in terraform-local.tf.example.
# Copy that file to terraform-local.tf.

terraform {
  required_version = "~> 0.15.0"

  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.1.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.36.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
  }
}
