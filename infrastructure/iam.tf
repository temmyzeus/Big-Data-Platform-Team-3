resource "aws_iam_user" "s3_user" {
  name = "s3_user"

  tags = {
    tag-key = "prod"
  }
}

data "aws_iam_policy_document" "s3_user_policy_doc" {
  statement {
    effect = "Allow"
    actions = ["s3:GetObject",
      "s3:PutObjectAcl",
      "s3:PutObject",
      "s3:ListAllMyBuckets",
      "s3:ListBucket"
    ]
    resources = [
        "arn:aws:s3:::big-data-platform-team-3/*", 
    "arn:aws:s3:::big-data-platform-team-3"]
  }
}

resource "aws_iam_user_policy" "s3_user_policy" {
  name   = "s3_write_and_list_access"
  user   = aws_iam_user.s3_user.name
  policy = data.aws_iam_policy_document.s3_user_policy_doc.json
}