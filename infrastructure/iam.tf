resource "aws_iam_user" "s3_user" {
  name = "s3_user"
  
  tags = {
    tag-key = "prod"
  }
}

# resource "aws_iam_access_key" "lb" {
#   user = aws_iam_user.lb.name
# }

data "aws_iam_policy_document" "s3_user_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = ["s3:GetObject",
    "s3PutObjectAcl",
    "s3:PutObject", 
    "s3:ListObject"
    ]
    resources = ["arn:aws:s3:::big-data-platform-team-3/*"]
  }
}

resource "aws_iam_user_policy" "s3_user_policy" {
  name   = "iam"
  user   = aws_iam_user.s3_user.name
  policy = data.aws_iam_policy_document.s3_user_policy_doc.json
}