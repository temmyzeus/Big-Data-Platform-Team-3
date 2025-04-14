# Terraform Remote State
terraform {
  backend "s3" {
    bucket = "emr-state-bucket"
    key    = "key/terraform.tfstate"
    region = "us-east-1"
  }
}
