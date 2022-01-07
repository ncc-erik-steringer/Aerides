/*
  Infracode for the finance department. For this demo, the finance
  resources are tagged with the "finance" component.
*/

resource "aws_s3_bucket" "service_ledger" {
  bucket = "tktk-service-ledger"
  acl = "private"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Deny"
        Principal = "*"
        Action = "s3:GetObject*"
        Resource = "arn:aws:s3:::tktk-service-ledger/*"
        Condition = {
          StringNotEquals = {
            "aws:PrincipalTag/dept" = "finance"
          }
        }
      }
    ]
  })
}

resource "aws_iam_user" "finance_user_warren" {
  name = "warren"
  tags = {
    dept = "finance"
  }
}

resource "aws_iam_user_policy" "finance_user_warren_perms" {
  name = "warren-permissions-1"
  user = aws_iam_user.finance_user_warren.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:GetObject*"
        Resource = "arn:aws:s3:::tktk-service-ledger/inbox/*"
      },
      {
        Effect = "Allow"
        Action = "s3:PutObject"
        Resource = "arn:aws:s3:::tktk-service-ledger/outbox/*"
      }
    ]
  })
}

