# Terraform Remote State
terraform {
  backend "s3" {
    bucket = "big-data-platform-team-3-state"
    key    = "key/terraform.tfstate"
    region = "us-east-1"
    profile = "big-data-admin"
  }
}
