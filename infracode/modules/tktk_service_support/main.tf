/*
  Infracode for the support staff. For this demo, the support staff access the
  account through IAM Role Sessions (Cognito AuthN), while this code defines the IAM Role resource
  plus the associated policy.
*/

resource "aws_iam_role" "support_iam_role" {
  name = "support-staff"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = "us-east:12345678-ffff-ffff-ffff-123456"
          }
        }
      }
    ]
  })
  tags = {
    dept = "support"
  }
}

resource "aws_iam_role_policy" "support_iam_role_policy" {
  name = "support-permissions-1"
  role = aws_iam_role.support_iam_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "autoscaling:Get*",
          "elasticloadbalancing:List*",
          "elasticloadbalancing:Get*"
        ],
        Resource = "*"
      }
    ]
  })
}

