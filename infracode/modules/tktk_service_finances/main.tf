#  Copyright (c) 2022 Erik Steringer and NCC Group
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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

