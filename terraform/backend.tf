terraform {
  backend "s3" {
    # Configure these values via backend config file or CLI
    # bucket         = "your-terraform-state-bucket"
    # key            = "serverless-health-check/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-state-lock"
    # encrypt        = true
  }
}