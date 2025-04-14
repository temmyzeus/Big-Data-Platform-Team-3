resource "aws_s3_bucket" "emr-bucket" {
  bucket = "big-data-platform-team-3"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_object" "input_object" {
  bucket = "big-data-platform-team-3"
  key    = "input_files"
  source = "big-data-platform-team-3/input_files"

}