/*
  Infracode for IAM Users/Roles. For this demo, there will be a few
  IAM Users that represent operators/administrators over the infrastructure
  and a few IAM Roles for support personnel.
*/

// region Account Admins

/*
  These IAM Users are the admins of the AWS account, with the AdministratorAccess policy
  and the admin dept tag. They have permissions granted via IAM Group membership.
*/

resource "aws_iam_group" "account_admins" {
  name = "admins"
}

resource "aws_iam_group_policy_attachment" "admin_to_admins" {
  group = aws_iam_group.account_admins.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_user" "admin_erik" {
  name = "erik"
  tags = {
    dept = "admin"
  }
}

resource "aws_iam_user" "admin_mary" {
  name = "mary"
  tags = {
    dept = "admin"
  }
}

resource "aws_iam_group_membership" "admins_memberships" {
  name = "admin_group_memberships"
  users = [
    aws_iam_user.admin_erik.name,
    aws_iam_user.admin_mary.name
  ]
  group = aws_iam_group.account_admins.name
}

// endregion Account Admins

// region Operators

/*
  These IAM Users are operators in the AWS account, with the a custom policy
  and the operator dept tag. They have permissions granted via IAM Group membership, which
  are limited to EC2/AutoScaling/DDB/ELB
*/

resource "aws_iam_group" "account_operators" {
  name = "operators"
}

resource "aws_iam_group_policy" "operator_policy" {
  name = "operator-policy"
  group = aws_iam_group.account_operators.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "autoscaling:*",
          "dynamodb:*",
          "elasticloadbalancing:*"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = "iam:PassRole",
        Resource = "*",
        Condition = {
          "StringEquals" = {
            "iam:PassedToService": "ec2.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_iam_user" "operator_frank" {
  name = "frank"
  tags = {
    dept = "operators"
  }
}

resource "aws_iam_user" "operator_john" {
  name = "john"
  tags = {
    dept = "operators"
  }
}

resource "aws_iam_user" "operator_adam" {
  name = "adam"
  tags = {
    dept = "operators"
  }
}

resource "aws_iam_group_membership" "admin_memberships" {
  name = "admin_group_memberships"
  users = [
    aws_iam_user.operator_frank.name,
    aws_iam_user.operator_john.name,
    aws_iam_user.operator_adam.name
  ]
  group = aws_iam_group.account_operators.name
}

// endregion Operators
