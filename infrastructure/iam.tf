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

resource "aws_iam_role" "emr_service_role" {
  name               = "emr-service-role"
  assume_role_policy = data.aws_iam_policy_document.emr_assume_role.json
}

data "aws_iam_policy_document" "emr_service_policy" {
  statement {
    effect = "Allow"

    actions = [
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:CancelSpotInstanceRequests",
      "ec2:CreateNetworkInterface",
      "ec2:CreateSecurityGroup",
      "ec2:CreateTags",
      "ec2:DeleteNetworkInterface",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteTags",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeAccountAttributes",
      "ec2:DescribeDhcpOptions",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeInstances",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeNetworkAcls",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribePrefixLists",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSpotInstanceRequests",
      "ec2:DescribeSpotPriceHistory",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcAttribute",
      "ec2:DescribeVpcEndpoints",
      "ec2:DescribeVpcEndpointServices",
      "ec2:DescribeVpcs",
      "ec2:DetachNetworkInterface",
      "ec2:ModifyImageAttribute",
      "ec2:ModifyInstanceAttribute",
      "ec2:RequestSpotInstances",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:RunInstances",
      "ec2:TerminateInstances",
      "ec2:DeleteVolume",
      "ec2:DescribeVolumeStatus",
      "ec2:DescribeVolumes",
      "ec2:DetachVolume",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListInstanceProfiles",
      "iam:ListRolePolicies",
      "iam:PassRole",
      "s3:CreateBucket",
      "s3:Get*",
      "s3:List*",
      "sdb:BatchPutAttributes",
      "sdb:Select",
      "sqs:CreateQueue",
      "sqs:Delete*",
      "sqs:GetQueue*",
      "sqs:PurgeQueue",
      "sqs:ReceiveMessage",
    ]

    resources = ["*"]
  }
}


resource "aws_iam_role_policy" "iam_emr_service_policy" {
  name   = "iam_emr_service_policy"
  role   = aws_iam_role.emr_service_role.id
  policy = data.aws_iam_policy_document.emr_service_policy.json
}


data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "emr_profile_role" {
  name               = "emr-instance-profile-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

resource "aws_iam_instance_profile" "emr_profile" {
  name = "emr_instance_profile"
  role = aws_iam_role.emr_profile_role.name
}


data "aws_iam_policy_document" "emr_instance_profile_policy" {
  statement {
    effect = "Allow"

    actions = [
      "cloudwatch:*",
      "dynamodb:*",
      "ec2:Describe*",
      "elasticmapreduce:Describe*",
      "elasticmapreduce:ListBootstrapActions",
      "elasticmapreduce:ListClusters",
      "elasticmapreduce:ListInstanceGroups",
      "elasticmapreduce:ListInstances",
      "elasticmapreduce:ListSteps",
      "elasticmapreduce:RunJobFlow", # ADDED THIS
      "kinesis:CreateStream",
      "kinesis:DeleteStream",
      "kinesis:DescribeStream",
      "kinesis:GetRecords",
      "kinesis:GetShardIterator",
      "kinesis:MergeShards",
      "kinesis:PutRecord",
      "kinesis:SplitShard",
      "rds:Describe*",
      "s3:*",
      "sdb:*",
      "sns:*",
      "sqs:*",
    ]

    resources = ["*"]
  }
}


resource "aws_iam_role_policy" "emr_instance_profile_policy" {
  name   = "emr_instance_profile_policy"
  role   = aws_iam_role.emr_profile_role.id
  policy = data.aws_iam_policy_document.emr_instance_profile_policy.json
}
