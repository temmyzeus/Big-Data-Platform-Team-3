resource "aws_s3_bucket" "emr-bucket" {
  # bucket = "big-data-platform-team-3"
  bucket = "big-data-platform-team-3a"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
