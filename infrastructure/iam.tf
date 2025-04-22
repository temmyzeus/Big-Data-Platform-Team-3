resource "aws_iam_user" "s3_user" {
  name = "s3_user"

   tags = {
    Environment = "Production"
    Owner = "Data Platform Team"
    Service = "s3"
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

resource "aws_iam_user" "airflow_user" {
  name = "airflow_user"

  tags = {
    Environment = "Production"
    Owner = "Data Platform Team"
    Service = "Airflow"
  }
}

resource "aws_iam_access_key" "airflow_keys" {
  user = aws_iam_user.airflow_user.name
}


resource "aws_ssm_parameter" "airflow_access_key" {
  name  = "/Production/airflow/aws_access_key"
  type  = "String"
  value = aws_iam_access_key.airflow_keys.id
}

resource "aws_ssm_parameter" "airflow_access_key" {
  name  = "/Production/airflow/aws_access_key"
  type  = "String"
  value = aws_iam_access_key.airflow_keys.secret
}

data "aws_iam_policy_document" "emr_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["elasticmapreduce.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}






